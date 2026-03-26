"""
codex_django.booking.selectors
===============================
Pure-function selectors for booking operations.

These are the high-level entry points for views and CLI-generated features.
The adapter is passed as an argument (dependency injection).

Rules enforced:
    R1 — Cache invalidation via ``transaction.on_commit()`` only.
    R2 — ``lock_masters()`` uses ``select_for_update(of=('self',))``.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from django.db import transaction

from codex_services.booking.slot_master.chain_finder import ChainFinder
from codex_services.booking.slot_master.dto import EngineResult
from codex_services.booking.slot_master import SlotAlreadyBookedError

if TYPE_CHECKING:
    from codex_django.booking.adapters.availability import DjangoAvailabilityAdapter
    from codex_django.booking.adapters.cache import BookingCacheAdapter


def get_available_slots(
    adapter: DjangoAvailabilityAdapter,
    service_ids: list[int],
    target_date: date,
    *,
    locked_master_id: int | None = None,
    master_selections: dict[str, str] | None = None,
    max_solutions: int = 50,
    max_unique_starts: int | None = None,
    cache_ttl: int = 300,
) -> EngineResult:
    """Compute available booking slots for a given date.

    Builds the engine request, fetches master availability, and runs
    ``ChainFinder.find()``.
    """
    request = adapter.build_engine_request(
        service_ids=service_ids,
        target_date=target_date,
        locked_master_id=locked_master_id,
        master_selections=master_selections,
    )

    all_master_ids: list[int] = []
    for sr in request.service_requests:
        all_master_ids.extend(int(mid) for mid in sr.possible_resource_ids)
    unique_master_ids = list(set(all_master_ids))

    availability = adapter.build_masters_availability(
        master_ids=unique_master_ids,
        target_date=target_date,
        cache_ttl=cache_ttl,
    )

    finder = ChainFinder(step_minutes=adapter.step_minutes)
    return finder.find(
        request=request,
        resources_availability=availability,
        max_solutions=max_solutions,
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


def get_nearest_slots(
    adapter: DjangoAvailabilityAdapter,
    service_ids: list[int],
    search_from: date,
    *,
    locked_master_id: int | None = None,
    master_selections: dict[str, str] | None = None,
    search_days: int = 60,
    max_solutions_per_day: int = 1,
) -> EngineResult:
    """Search for the nearest available date with open slots (waitlist).

    Uses ``ChainFinder.find_nearest()`` which scans forward day by day.
    """
    request = adapter.build_engine_request(
        service_ids=service_ids,
        target_date=search_from,
        locked_master_id=locked_master_id,
        master_selections=master_selections,
    )

    def get_availability_for_date(
        d: date,
    ) -> dict[str, Any]:
        all_master_ids: list[int] = []
        for sr in request.service_requests:
            all_master_ids.extend(int(mid) for mid in sr.possible_resource_ids)
        return adapter.build_masters_availability(
            master_ids=list(set(all_master_ids)),
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
    master_id: int,
    client: Any,
    extra_fields: dict[str, Any] | None = None,
) -> Any:
    """Create a booking with concurrency protection.

    1. Locks the master row (R2: ``select_for_update(of=('self',))``)
    2. Re-checks slot availability under lock
    3. Creates the appointment
    4. Invalidates cache after commit (R1: ``transaction.on_commit()``)

    Raises ``SlotAlreadyBookedError`` if the slot was taken.
    """
    with transaction.atomic():
        adapter.lock_masters([master_id])

        result = get_available_slots(
            adapter=adapter,
            service_ids=service_ids,
            target_date=target_date,
            locked_master_id=master_id,
            cache_ttl=0,  # no cache under lock — fresh data
        )

        available_times = result.get_unique_start_times()
        if selected_time not in available_times:
            raise SlotAlreadyBookedError(
                f"Slot {selected_time} on {target_date} is no longer available."
            )

        # Find the matching solution for duration info
        best = result.best
        if best is None:
            raise SlotAlreadyBookedError("No solution found.")

        fields: dict[str, Any] = {
            "master_id": master_id,
            "datetime_start": best.starts_at,
            "duration_minutes": best.span_minutes,
            "client": client,
        }
        if extra_fields:
            fields.update(extra_fields)

        appointment = appointment_model.objects.create(**fields)

        # R1: invalidate cache AFTER transaction commits
        _master_id_str = str(master_id)
        _date_str = str(target_date)
        transaction.on_commit(
            lambda: cache_adapter.invalidate_master_date(
                _master_id_str, _date_str
            )
        )

    return appointment
