"""
codex_django.booking.selectors
===============================
Pure-function selectors for booking operations.

These are the high-level entry points for views and CLI-generated features.
The adapter is passed as an argument (dependency injection).

Rules enforced:
    R1 — Cache invalidation via ``transaction.on_commit()`` only.
    R2 — ``lock_resources()`` uses ``select_for_update(of=('self',))``.
"""

from __future__ import annotations

import json
from calendar import monthrange
from collections.abc import Mapping
from datetime import date
from typing import TYPE_CHECKING, Any, Protocol

from codex_services.booking.slot_master import SlotAlreadyBookedError
from codex_services.booking.slot_master.chain_finder import ChainFinder
from codex_services.booking.slot_master.dto import EngineResult
from codex_services.booking.slot_master.modes import BookingMode
from django.db import transaction

if TYPE_CHECKING:
    from codex_django.booking.adapters.availability import DjangoAvailabilityAdapter
    from codex_django.booking.adapters.cache import BookingCacheAdapter


ResourceSelections = dict[str, str] | dict[int, int | None] | None
SINGLE_SERVICE_DEFAULT_MAX_SOLUTIONS = 50
MULTI_SERVICE_DEFAULT_MAX_SOLUTIONS = 2000


class BookingPersistenceHook(Protocol):
    """Protocol for project-specific multi-service persistence."""

    def persist_chain(
        self,
        solution: Any,
        service_ids: list[int],
        client: Any,
        extra_fields: dict[str, Any] | None = None,
    ) -> list[Any]:
        """Persist a multi-service chain and return appointment-like objects."""
        ...


def get_available_slots(
    adapter: DjangoAvailabilityAdapter,
    service_ids: list[int],
    target_date: date,
    *,
    locked_resource_id: int | None = None,
    resource_selections: ResourceSelections = None,
    mode: BookingMode = BookingMode.SINGLE_DAY,
    overlap_allowed: bool = False,
    parallel_groups: dict[int, str] | None = None,
    max_solutions: int | None = None,
    max_unique_starts: int | None = None,
    cache_ttl: int = 300,
) -> EngineResult:
    """Compute available booking slots for a given date.

    Builds the engine request, fetches master availability, and runs
    ``ChainFinder.find()``.

    Args:
        adapter: Availability adapter that bridges Django models to the engine.
        service_ids: Ordered list of requested service identifiers.
        target_date: Date for which slots should be computed.
        locked_resource_id: Optional resource id that constrains the search.
        resource_selections: Optional per-service resource selection mapping.
        mode: Booking engine search mode.
        overlap_allowed: Whether services may overlap in time.
        parallel_groups: Optional mapping of service id to parallel group id.
        max_solutions: Maximum number of engine solutions to compute. Defaults
            to 50 for single-service requests and 2000 for multi-service chains.
        max_unique_starts: Optional cap for unique start times.
        cache_ttl: Cache lifetime in seconds for busy-slot reads.

    Returns:
        Engine result produced by ``ChainFinder.find()``.
    """
    request = adapter.build_engine_request(
        service_ids=service_ids,
        target_date=target_date,
        locked_resource_id=locked_resource_id,
        resource_selections=resource_selections,
        mode=mode,
        overlap_allowed=overlap_allowed,
        parallel_groups=parallel_groups,
    )

    all_resource_ids: list[int] = []
    for sr in request.service_requests:
        all_resource_ids.extend(int(mid) for mid in sr.possible_resource_ids)
    unique_resource_ids = list(set(all_resource_ids))

    availability = adapter.build_resources_availability(
        resource_ids=unique_resource_ids,
        target_date=target_date,
        cache_ttl=cache_ttl,
    )

    effective_max_solutions = _get_effective_max_solutions(service_ids, max_solutions)

    finder = ChainFinder(step_minutes=adapter.step_minutes)
    return finder.find(
        request=request,
        resources_availability=availability,
        max_solutions=effective_max_solutions,
        max_unique_starts=max_unique_starts,
    )


def get_calendar_data(
    year: int,
    month: int,
    today: date | None = None,
    selected_date: date | None = None,
    holidays_subdiv: str = "ST",
) -> list[dict[str, Any]]:
    """Generate a calendar month matrix for UI rendering.

    Wraps ``CalendarEngine.get_month_matrix()`` from codex-services.

    Args:
        year: Target calendar year.
        month: Target calendar month.
        today: Optional date used to highlight the current day.
        selected_date: Optional date selected in the UI.
        holidays_subdiv: Region code passed to the calendar engine.

    Returns:
        Calendar matrix data ready for template rendering.
    """
    from codex_services.calendar.engine import CalendarEngine

    if today is None:
        today = date.today()

    return CalendarEngine.get_month_matrix(
        year=year,
        month=month,
        today=today,
        selected_date=selected_date,
        holidays_subdiv=holidays_subdiv,
    )


def build_month_grid_cells(year: int, month: int, visible_days: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Expand visible month days into a 7-column calendar grid.

    The cabinet date-time picker expects a Monday-first month grid. Some
    upstream calendar payloads expose only the visible days for the current
    month, which makes the first week shift left when the month starts on a
    later weekday. This helper pads the visible days with leading and trailing
    blank cells so templates can render a stable 7-column matrix.

    Args:
        year: Target calendar year.
        month: Target calendar month.
        visible_days: Flat list of day payloads for the given month.

    Returns:
        A list of calendar cell dicts. Blank placeholders include
        ``{"blank": True}``; real day payloads are copied and annotated with
        ``blank=False``.
    """
    if not visible_days:
        return []

    first_weekday, month_days = monthrange(year, month)
    month_payload = visible_days[:month_days]
    leading_blanks = first_weekday
    trailing_blanks = (-((leading_blanks + len(month_payload)) % 7)) % 7

    cells: list[dict[str, Any]] = [{"blank": True} for _ in range(leading_blanks)]
    cells.extend({**day, "blank": False} for day in month_payload)
    cells.extend({"blank": True} for _ in range(trailing_blanks))
    return cells


def build_picker_day_rows(
    *,
    start_date: date,
    horizon: int,
    available_dates: set[str],
    has_service_scope: bool = True,
) -> list[dict[str, str | int | bool]]:
    """Build booking day-picker rows with month headers and blank paddings.

    This helper mirrors the cabinet date-picker payload shape used by booking
    workflows. It keeps month grouping and leading blank cell generation in one
    reusable place so project services don't reimplement this rendering contract.
    """
    rows: list[dict[str, str | int | bool]] = []
    if horizon <= 0:
        return rows

    current_month_key: str | None = None
    for offset in range(horizon):
        current_date = start_date.fromordinal(start_date.toordinal() + offset)
        month_key = current_date.strftime("%Y-%m")
        month_label = current_date.strftime("%B %Y")
        if month_key != current_month_key:
            for blank_index in range(current_date.weekday()):
                rows.append(
                    {
                        "day": "",
                        "iso": f"{month_key}-blank-{blank_index}",
                        "busy": True,
                        "available": False,
                        "label": "",
                        "month_key": month_key,
                        "month_label": month_label,
                    }
                )
            current_month_key = month_key

        iso = current_date.isoformat()
        is_available = iso in available_dates if has_service_scope else False
        rows.append(
            {
                "day": current_date.day,
                "iso": iso,
                "busy": has_service_scope and not is_available,
                "available": is_available,
                "label": current_date.strftime("%b %d, %Y"),
                "month_key": month_key,
                "month_label": month_label,
            }
        )
    return rows


def parse_resource_selections(raw_value: str | None) -> dict[str, str] | None:
    """Parse serialized resource selections from HTTP payloads.

    Accepts a JSON object and drops non-selections (``any``, empty, ``null``).
    Returns ``None`` when the payload is missing, invalid, or produces no
    effective selections.
    """
    if not raw_value:
        return None
    try:
        parsed = json.loads(raw_value)
    except Exception:
        return None
    if not isinstance(parsed, dict):
        return None

    normalized: dict[str, str] = {}
    for key, value in parsed.items():
        if value in ("", None, "any"):
            continue
        normalized[str(key)] = str(value)
    return normalized or None


def normalize_slot_payload(payload: Any) -> list[str]:
    """Normalize slot payloads from booking gateway calls.

    Supports engine results (``get_unique_start_times``), ``dict`` payloads
    like ``{slot: allowed}``, and plain iterables of slot strings.
    """
    if payload is None:
        return []

    get_unique_start_times = getattr(payload, "get_unique_start_times", None)
    if callable(get_unique_start_times):
        try:
            return sorted({str(slot) for slot in get_unique_start_times() if str(slot)})
        except Exception:
            return []

    if isinstance(payload, Mapping):
        return sorted(str(slot) for slot, allowed in payload.items() if allowed)

    if isinstance(payload, list | tuple | set):
        return sorted(str(slot) for slot in payload if str(slot))

    return []


def get_nearest_slots(
    adapter: DjangoAvailabilityAdapter,
    service_ids: list[int],
    search_from: date,
    *,
    locked_resource_id: int | None = None,
    resource_selections: ResourceSelections = None,
    mode: BookingMode = BookingMode.SINGLE_DAY,
    overlap_allowed: bool = False,
    parallel_groups: dict[int, str] | None = None,
    search_days: int = 60,
    max_solutions_per_day: int = 1,
) -> EngineResult:
    """Search for the nearest available date with open slots (waitlist).

    Uses ``ChainFinder.find_nearest()`` which scans forward day by day.

    Args:
        adapter: Availability adapter that bridges Django models to the engine.
        service_ids: Ordered list of requested service identifiers.
        search_from: First date included in the forward search.
        locked_resource_id: Optional resource id that constrains the search.
        resource_selections: Optional per-service resource selection mapping.
        mode: Booking engine search mode.
        overlap_allowed: Whether services may overlap in time.
        parallel_groups: Optional mapping of service id to parallel group id.
        search_days: Number of forward days to inspect.
        max_solutions_per_day: Maximum number of solutions evaluated per day.

    Returns:
        Engine result produced by ``ChainFinder.find_nearest()``.
    """
    request = adapter.build_engine_request(
        service_ids=service_ids,
        target_date=search_from,
        locked_resource_id=locked_resource_id,
        resource_selections=resource_selections,
        mode=mode,
        overlap_allowed=overlap_allowed,
        parallel_groups=parallel_groups,
    )

    def get_availability_for_date(
        d: date,
    ) -> dict[str, Any]:
        all_resource_ids: list[int] = []
        for sr in request.service_requests:
            all_resource_ids.extend(int(mid) for mid in sr.possible_resource_ids)
        return adapter.build_resources_availability(
            resource_ids=list(set(all_resource_ids)),
            target_date=d,
        )

    finder = ChainFinder(step_minutes=adapter.step_minutes)
    return finder.find_nearest(
        request=request,
        get_availability_for_date=get_availability_for_date,
        search_from=search_from,
        search_days=search_days,
        max_solutions_per_day=max_solutions_per_day,
    )


def create_booking(
    adapter: DjangoAvailabilityAdapter,
    cache_adapter: BookingCacheAdapter,
    appointment_model: type[Any],
    *,
    service_ids: list[int],
    target_date: date,
    selected_time: str,
    resource_id: int | None,
    client: Any,
    extra_fields: dict[str, Any] | None = None,
    resource_selections: ResourceSelections = None,
    mode: BookingMode = BookingMode.SINGLE_DAY,
    overlap_allowed: bool = False,
    parallel_groups: dict[int, str] | None = None,
    max_solutions: int | None = None,
    persistence_hook: BookingPersistenceHook | None = None,
) -> Any | list[Any]:
    """Create a booking with concurrency protection.

    Locked-resource mode:
    1. Locks a single resource row
    2. Re-checks slot availability under lock
    3. Creates one appointment
    4. Invalidates cache after commit (R1: ``transaction.on_commit()``)

    Chain mode:
    1. Requires a ``persistence_hook``
    2. Locks all candidate resources for the chain
    3. Re-checks chain availability under lock
    4. Delegates persistence to ``persistence_hook.persist_chain()``
    5. Invalidates cache for chain masters after commit

    Args:
        adapter: Availability adapter used for locking and revalidation.
        cache_adapter: Cache adapter used for post-commit invalidation.
        appointment_model: Concrete Django model class for appointment rows.
        service_ids: Ordered list of requested service identifiers.
        target_date: Booking date selected by the client.
        selected_time: Selected start time in ``HH:MM`` format.
        resource_id: Resource chosen for single-service mode.
        client: Client object attached to the booking.
        extra_fields: Optional extra model fields passed to persistence.
        resource_selections: Optional per-service resource selection mapping.
        mode: Booking engine search mode.
        overlap_allowed: Whether services may overlap in time.
        parallel_groups: Optional mapping of service id to parallel group id.
        max_solutions: Optional cap for engine solutions during final
            revalidation. Defaults match ``get_available_slots()``.
        persistence_hook: Required persistence hook for multi-service mode.

    Returns:
        A single appointment instance in locked-resource mode, or a list of
        created appointment-like objects in chain mode.

    Raises:
        codex_services.booking.slot_master.SlotAlreadyBookedError: If the
            selected slot is no longer available under lock.
        NotImplementedError: If multi-service mode is requested without a
            persistence hook.
    """
    is_chain_flow = len(service_ids) > 1 or resource_id is None

    with transaction.atomic():
        if is_chain_flow:
            if len(service_ids) > 1 and persistence_hook is None:
                raise NotImplementedError("Multi-service persistence requires a persistence hook")

            request = adapter.build_engine_request(
                service_ids=service_ids,
                target_date=target_date,
                locked_resource_id=resource_id,
                resource_selections=resource_selections,
                mode=mode,
                overlap_allowed=overlap_allowed,
                parallel_groups=parallel_groups,
            )
            all_resource_ids: set[int] = {
                int(mid) for sr in request.service_requests for mid in sr.possible_resource_ids
            }
            adapter.lock_resources(sorted(all_resource_ids))

            result = get_available_slots(
                adapter=adapter,
                service_ids=service_ids,
                target_date=target_date,
                locked_resource_id=resource_id,
                resource_selections=resource_selections,
                mode=mode,
                overlap_allowed=overlap_allowed,
                parallel_groups=parallel_groups,
                max_solutions=max_solutions,
                cache_ttl=0,  # no cache under lock — fresh data
            )
            available_times = result.get_unique_start_times()
            if selected_time not in available_times:
                raise SlotAlreadyBookedError(f"Slot {selected_time} on {target_date} is no longer available.")

            selected_solution = _select_solution_for_time(result, selected_time)
            if selected_solution is None:
                raise SlotAlreadyBookedError("No solution found.")

            if persistence_hook is not None:
                created_appointments = persistence_hook.persist_chain(
                    solution=selected_solution,
                    service_ids=service_ids,
                    client=client,
                    extra_fields=extra_fields,
                )
            else:
                # Generic fallback for single-service "any resource" flows.
                primary_item = next(iter(getattr(selected_solution, "items", [])), None)
                if primary_item is None:
                    raise SlotAlreadyBookedError("No solution found.")
                created_appointments = [
                    _create_single_appointment(
                        appointment_model=appointment_model,
                        resource_id=int(primary_item.resource_id),
                        service_ids=service_ids,
                        starts_at=selected_solution.starts_at,
                        span_minutes=selected_solution.span_minutes,
                        client=client,
                        extra_fields=extra_fields,
                    )
                ]

            chain_resource_ids = {
                str(item.resource_id)
                for item in getattr(selected_solution, "items", [])
                if getattr(item, "resource_id", None)
            }
            if not chain_resource_ids and resource_id is not None:
                chain_resource_ids = {str(resource_id)}

            _date_str = str(target_date)

            def _invalidate_many() -> None:
                for mid in chain_resource_ids:
                    cache_adapter.invalidate_master_date(mid, _date_str)

            transaction.on_commit(_invalidate_many)
            return created_appointments

        if resource_id is None:
            raise SlotAlreadyBookedError("Resource id is required for single-resource booking flow.")

        adapter.lock_resources([resource_id])

        result = get_available_slots(
            adapter=adapter,
            service_ids=service_ids,
            target_date=target_date,
            locked_resource_id=resource_id,
            resource_selections=resource_selections,
            mode=mode,
            overlap_allowed=overlap_allowed,
            parallel_groups=parallel_groups,
            max_solutions=max_solutions,
            cache_ttl=0,  # no cache under lock — fresh data
        )

        available_times = result.get_unique_start_times()
        if selected_time not in available_times:
            raise SlotAlreadyBookedError(f"Slot {selected_time} on {target_date} is no longer available.")

        # Find the matching solution for duration info.
        selected_solution = _select_solution_for_time(result, selected_time)
        if selected_solution is None:
            raise SlotAlreadyBookedError("No solution found.")

        appointment = _create_single_appointment(
            appointment_model=appointment_model,
            resource_id=resource_id,
            service_ids=service_ids,
            starts_at=selected_solution.starts_at,
            span_minutes=selected_solution.span_minutes,
            client=client,
            extra_fields=extra_fields,
        )

        # R1: invalidate cache AFTER transaction commits
        _resource_id_str = str(resource_id)
        _date_str = str(target_date)
        transaction.on_commit(lambda: cache_adapter.invalidate_master_date(_resource_id_str, _date_str))

    return appointment


def _get_effective_max_solutions(service_ids: list[int], max_solutions: int | None) -> int:
    if max_solutions is not None:
        return max_solutions
    if len(service_ids) > 1:
        return MULTI_SERVICE_DEFAULT_MAX_SOLUTIONS
    return SINGLE_SERVICE_DEFAULT_MAX_SOLUTIONS


def _select_solution_for_time(result: EngineResult, selected_time: str) -> Any | None:
    for solution in result.solutions:
        if solution.starts_at.strftime("%H:%M") == selected_time:
            return solution
    return None


def _create_single_appointment(
    *,
    appointment_model: type[Any],
    resource_id: int,
    service_ids: list[int],
    starts_at: Any,
    span_minutes: int,
    client: Any,
    extra_fields: dict[str, Any] | None,
) -> Any:
    fields: dict[str, Any] = {
        "datetime_start": starts_at,
        "duration_minutes": span_minutes,
        "client": client,
    }
    if extra_fields:
        fields.update(extra_fields)

    meta = getattr(appointment_model, "_meta", None)
    attnames: set[str] = set()
    if meta is not None:
        attnames = {field.attname for field in meta.fields}

    if "resource_id" in attnames:
        fields["resource_id"] = resource_id
    else:
        fields["master_id"] = resource_id

    if len(service_ids) == 1 and "service_id" in attnames:
        fields["service_id"] = service_ids[0]

    return appointment_model.objects.create(**fields)
