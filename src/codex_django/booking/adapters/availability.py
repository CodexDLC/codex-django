"""
codex_django.booking.adapters.availability
===========================================
Universal bridge between Django ORM and the codex-services booking engine.

All models are injected at construction time — no hardcoded imports.

Rules enforced:
    R1 — Cache invalidation via ``transaction.on_commit()`` only (see selectors).
    R2 — ``select_for_update(of=('self',))`` in ``lock_masters()``.
    R3 — No clean/save overrides here; pure adapter logic.
"""

from __future__ import annotations

import zoneinfo
from datetime import UTC, date, datetime, timedelta
from typing import Any

from codex_services.booking._shared.calculator import SlotCalculator
from codex_services.booking.slot_master.dto import (
    BookingEngineRequest,
    EngineResult,
    MasterAvailability,
    ServiceRequest,
)
from codex_services.booking.slot_master.modes import BookingMode

from codex_django.booking.adapters.cache import BookingCacheAdapter


class DjangoAvailabilityAdapter:
    """Universal bridge between Django ORM and the booking engine.

    Implements the three provider interfaces from codex-services so it
    can be used directly with ``ChainFinder``.

    Args:
        master_model: Django model class for masters/resources.
        appointment_model: Django model class for appointments.
        service_model: Django model class for services.
        working_day_model: Django model class for per-weekday schedule.
        day_off_model: Django model class for days off.
        booking_settings_model: Django model class for booking settings.
        site_settings_model: Django model class for site-level settings.
        step_minutes: Time grid step for the engine.
        appointment_status_filter: Which statuses count as "busy".
        cache_adapter: Optional cache adapter; defaults to BookingCacheAdapter.
    """

    def __init__(
        self,
        master_model: type[Any],
        appointment_model: type[Any],
        service_model: type[Any],
        working_day_model: type[Any],
        day_off_model: type[Any],
        booking_settings_model: type[Any],
        site_settings_model: type[Any],
        step_minutes: int = 30,
        appointment_status_filter: list[str] | None = None,
        cache_adapter: BookingCacheAdapter | None = None,
    ) -> None:
        self.master_model = master_model
        self.appointment_model = appointment_model
        self.service_model = service_model
        self.working_day_model = working_day_model
        self.day_off_model = day_off_model
        self.booking_settings_model = booking_settings_model
        self.site_settings_model = site_settings_model

        self.step_minutes = step_minutes
        self._calc = SlotCalculator(step_minutes)
        self._cache = cache_adapter or BookingCacheAdapter()

        if appointment_status_filter:
            self.appointment_status_filter = appointment_status_filter
        else:
            self.appointment_status_filter = [
                getattr(appointment_model, "STATUS_PENDING", "pending"),
                getattr(appointment_model, "STATUS_CONFIRMED", "confirmed"),
            ]
            if hasattr(appointment_model, "STATUS_RESCHEDULE_PROPOSED"):
                self.appointment_status_filter.append(appointment_model.STATUS_RESCHEDULE_PROPOSED)

        self._booking_settings: Any = None
        self._site_settings: Any = None

    # ------------------------------------------------------------------
    # Engine request builder
    # ------------------------------------------------------------------

    def build_engine_request(
        self,
        service_ids: list[int],
        target_date: date,
        locked_master_id: int | None = None,
        master_selections: dict[str, str] | dict[int, int | None] | None = None,
        mode: BookingMode = BookingMode.SINGLE_DAY,
        overlap_allowed: bool = False,
        parallel_groups: dict[int, str] | None = None,
    ) -> BookingEngineRequest:
        """Build a ``BookingEngineRequest`` from DB service/master data."""
        services = self.service_model.objects.filter(id__in=service_ids).select_related("category")
        service_map = {s.id: s for s in services}
        normalized_master_selections = self._normalize_master_selections(service_ids, master_selections)

        weekday = target_date.weekday()
        service_requests: list[ServiceRequest] = []

        for svc_id in service_ids:
            service = service_map.get(svc_id)
            if not service:
                continue

            possible_ids = self._resolve_master_ids(
                service=service,
                weekday=weekday,
                locked_master_id=locked_master_id,
                master_selections=normalized_master_selections,
                service_id=svc_id,
            )
            if not possible_ids:
                continue

            gap = getattr(service, "min_gap_after_minutes", 0) or 0
            parallel_group = (parallel_groups or {}).get(svc_id)
            if parallel_group is None:
                parallel_group = getattr(service, "parallel_group", None) or None

            service_requests.append(
                ServiceRequest(
                    service_id=str(svc_id),
                    duration_minutes=service.duration,
                    min_gap_after_minutes=gap,
                    possible_resource_ids=possible_ids,
                    parallel_group=parallel_group,
                )
            )

        return BookingEngineRequest(
            service_requests=service_requests,
            booking_date=target_date,
            mode=mode,
            overlap_allowed=overlap_allowed,
        )

    # ------------------------------------------------------------------
    # Availability builder (implements AvailabilityProvider pattern)
    # ------------------------------------------------------------------

    def build_masters_availability(
        self,
        master_ids: list[int],
        target_date: date,
        cache_ttl: int = 0,
        exclude_appointment_ids: list[int] | None = None,
    ) -> dict[str, MasterAvailability]:
        """Build ``MasterAvailability`` dicts from ORM data.

        Caches **busy intervals** (not free slots) per master+date.
        """
        settings = self._get_booking_settings()
        result: dict[str, MasterAvailability] = {}

        # Days off — exclude these masters entirely
        day_off_ids = set(
            self.day_off_model.objects.filter(master_id__in=master_ids, date=target_date).values_list(
                "master_id", flat=True
            )
        )

        # Busy intervals (from appointments)
        busy_by_master = self._get_busy_intervals(master_ids, target_date, exclude_appointment_ids)

        masters = self.master_model.objects.filter(pk__in=master_ids)
        for master in masters:
            if master.pk in day_off_ids:
                continue

            working_hours_utc = self.get_working_hours(master, target_date)
            if not working_hours_utc:
                continue

            work_start_dt, work_end_dt = working_hours_utc
            break_interval = self.get_break_interval(master, target_date)
            buffer = self._get_buffer_minutes(master, settings)

            free_windows = self._calc.merge_free_windows(
                work_start=work_start_dt,
                work_end=work_end_dt,
                busy_intervals=busy_by_master.get(master.pk, []),
                break_interval=break_interval,
                buffer_minutes=buffer,
                min_duration_minutes=self.step_minutes,
            )

            result[str(master.pk)] = MasterAvailability(
                resource_id=str(master.pk),
                free_windows=free_windows,
                buffer_between_minutes=buffer,
            )

        return result

    # ------------------------------------------------------------------
    # Schedule (implements ScheduleProvider pattern)
    # ------------------------------------------------------------------

    def get_working_hours(self, master: Any, target_date: date) -> tuple[datetime, datetime] | None:
        """Return UTC working hours for a master on a specific date.

        Reads from ``working_day_model`` first; falls back to
        master-level defaults, then site-level defaults.
        """
        weekday = target_date.weekday()
        tz = self._get_tz(master)

        # 1. Per-day schedule from relational model
        working_day = self.working_day_model.objects.filter(master_id=master.pk, weekday=weekday).first()

        if working_day:
            start_t = working_day.start_time
            end_t = working_day.end_time
        else:
            # 2. Master-level defaults
            start_t = getattr(master, "work_start", None)
            end_t = getattr(master, "work_end", None)

        if not (start_t and end_t):
            # 3. Site-level defaults
            site = self._get_site_settings()
            if weekday < 5:
                start_t = getattr(site, "work_start_weekdays", None)
                end_t = getattr(site, "work_end_weekdays", None)
            elif weekday == 5:
                start_t = getattr(site, "work_start_saturday", None)
                end_t = getattr(site, "work_end_saturday", None)

        if not start_t or not end_t:
            return None

        work_start_dt = datetime.combine(target_date, start_t, tzinfo=tz)
        work_end_dt = datetime.combine(target_date, end_t, tzinfo=tz)
        return (work_start_dt.astimezone(UTC), work_end_dt.astimezone(UTC))

    def get_break_interval(self, master: Any, target_date: date) -> tuple[datetime, datetime] | None:
        """Return UTC break interval for a master on a date."""
        weekday = target_date.weekday()

        # Per-day schedule first
        working_day = self.working_day_model.objects.filter(master_id=master.pk, weekday=weekday).first()

        if working_day:
            break_start = working_day.break_start
            break_end = working_day.break_end
        else:
            break_start = getattr(master, "break_start", None)
            break_end = getattr(master, "break_end", None)

        if not (break_start and break_end):
            return None

        tz = self._get_tz(master)
        bs = datetime.combine(target_date, break_start, tzinfo=tz)
        be = datetime.combine(target_date, break_end, tzinfo=tz)
        return (bs.astimezone(UTC), be.astimezone(UTC))

    # ------------------------------------------------------------------
    # Locking (R2: select_for_update with of=('self',))
    # ------------------------------------------------------------------

    def lock_masters(self, master_ids: list[int]) -> None:
        """Acquire row-level locks on master records.

        Must be called inside ``transaction.atomic()``.
        IDs are sorted to prevent deadlocks.
        """
        if not master_ids:
            return
        sorted_ids = sorted(master_ids)
        list(self.master_model.objects.select_for_update(of=("self",)).filter(pk__in=sorted_ids).only("pk"))

    # ------------------------------------------------------------------
    # Busy intervals (implements BusySlotsProvider pattern)
    # ------------------------------------------------------------------

    def _get_busy_intervals(
        self,
        master_ids: list[int],
        target_date: date,
        exclude_appointment_ids: list[int] | None = None,
    ) -> dict[int, list[tuple[datetime, datetime]]]:
        """Fetch busy intervals from cache or DB."""
        busy_by_master: dict[int, list[tuple[datetime, datetime]]] = {mid: [] for mid in master_ids}

        appt_filter = {
            "master_id__in": master_ids,
            "datetime_start__date": target_date,
            "status__in": self.appointment_status_filter,
        }
        appointments_qs = self.appointment_model.objects.filter(**appt_filter)
        if exclude_appointment_ids:
            appointments_qs = appointments_qs.exclude(id__in=exclude_appointment_ids)
        appointments = appointments_qs.order_by("datetime_start")

        for app in appointments:
            s = app.datetime_start.astimezone(UTC).replace(second=0, microsecond=0)
            e = s + timedelta(minutes=app.duration_minutes)
            busy_by_master[app.master_id].append((s, e))

        return busy_by_master

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def result_to_slots_map(self, result: EngineResult) -> dict[str, bool]:
        """Convert engine result to a simple {HH:MM: True} map for templates."""
        times = result.get_unique_start_times()
        return dict.fromkeys(times, True)

    def _resolve_master_ids(
        self,
        service: Any,
        weekday: int,
        locked_master_id: int | None,
        master_selections: dict[int, int | None] | None,
        service_id: int,
    ) -> list[str]:
        """Determine which master IDs can perform a service."""
        if locked_master_id:
            return [str(locked_master_id)]

        if master_selections and service_id in master_selections:
            m_id = master_selections[service_id]
            if m_id is not None:
                return [str(m_id)]

        # All active masters for this service's category working on this weekday
        masters = self.master_model.objects.filter(
            categories=service.category,
            status=self.master_model.STATUS_ACTIVE,
        )

        # Filter by weekday using the relational working_day_model
        masters_with_schedule = set(
            self.working_day_model.objects.filter(
                master_id__in=masters.values_list("pk", flat=True),
                weekday=weekday,
            ).values_list("master_id", flat=True)
        )

        return [str(m.pk) for m in masters if m.pk in masters_with_schedule]

    def _normalize_master_selections(
        self,
        service_ids: list[int],
        master_selections: dict[str, str] | dict[int, int | None] | None,
    ) -> dict[int, int | None]:
        """Normalize legacy and new master selection formats.

        Supported input formats:
        - Legacy positional: {"0": "10", "1": "12"}
        - Service keyed: {5: 10, 7: None} or {"5": "10", "7": "12"}
        """
        if not master_selections:
            return {}

        # Legacy positional format: keys are indices inside service_ids.
        is_legacy_positional = all(
            isinstance(key, str) and key.isdigit() and int(key) < len(service_ids) for key in master_selections
        )
        if is_legacy_positional:
            normalized_legacy: dict[int, int | None] = {}
            for key, raw_val in master_selections.items():
                idx = int(key)
                if raw_val in (None, "any", ""):
                    continue
                if not isinstance(raw_val, str | int):
                    continue
                normalized_legacy[service_ids[idx]] = int(raw_val)
            return normalized_legacy

        normalized: dict[int, int | None] = {}
        for raw_key, raw_val in master_selections.items():
            service_id = int(raw_key)
            if raw_val in (None, "any", ""):
                normalized[service_id] = None
            else:
                if not isinstance(raw_val, str | int):
                    continue
                normalized[service_id] = int(raw_val)
        return normalized

    def _get_buffer_minutes(self, master: Any, settings: Any) -> int:
        individual = getattr(master, "buffer_between_minutes", None)
        if individual is not None:
            return individual  # type: ignore[no-any-return]
        return getattr(settings, "default_buffer_between_minutes", 0)

    def _get_tz(self, master: Any) -> zoneinfo.ZoneInfo:
        tz_name = getattr(master, "timezone", None)
        if not tz_name:
            site = self._get_site_settings()
            tz_name = getattr(site, "timezone", None) or "UTC"
        try:
            return zoneinfo.ZoneInfo(tz_name)
        except Exception:
            return zoneinfo.ZoneInfo("UTC")

    def _get_booking_settings(self) -> Any:
        if self._booking_settings is None:
            self._booking_settings = self.booking_settings_model.objects.first()
        return self._booking_settings

    def _get_site_settings(self) -> Any:
        if self._site_settings is None:
            self._site_settings = self.site_settings_model.objects.first()
        return self._site_settings
