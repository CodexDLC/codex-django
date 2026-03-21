"""
DjangoAvailabilityAdapter
=========================
Universal bridge between Django ORM and the booking engine.

Does NOT contain imports from specific project features.
Works with any models implementing the booking interface.

Requires: pip install codex-tools[django]
"""

import zoneinfo
from datetime import UTC, date, datetime, timedelta
from typing import Any

from codex_platform.booking.dto import (  # type: ignore[import-not-found]
    BookingEngineRequest,
    EngineResult,
    MasterAvailability,
    ServiceRequest,
)
from codex_platform.booking.modes import BookingMode  # type: ignore[import-not-found]
from codex_platform.calculator import SlotCalculator  # type: ignore[import-not-found]
from django.core.cache import cache


class DjangoAvailabilityAdapter:
    """
    Universal bridge between Django ORM and the booking engine.

    All models are passed upon initialization, making the adapter
    suitable for use in any project.
    """

    def __init__(
        self,
        master_model: type[Any],
        appointment_model: type[Any],
        service_model: type[Any],
        day_off_model: type[Any],
        booking_settings_model: type[Any],
        site_settings_model: type[Any],
        step_minutes: int = 30,
        appointment_status_filter: list[str] | None = None,
    ) -> None:
        self.master_model = master_model
        self.appointment_model = appointment_model
        self.service_model = service_model
        self.day_off_model = day_off_model
        self.booking_settings_model = booking_settings_model
        self.site_settings_model = site_settings_model

        self.step_minutes = step_minutes
        self._calc = SlotCalculator(step_minutes)

        if appointment_status_filter:
            self.appointment_status_filter = appointment_status_filter
        else:
            self.appointment_status_filter = [
                getattr(appointment_model, "STATUS_PENDING", "pending"),
                getattr(appointment_model, "STATUS_CONFIRMED", "confirmed"),
            ]
            if hasattr(appointment_model, "STATUS_RESCHEDULE_PROPOSED"):
                self.appointment_status_filter.append(appointment_model.STATUS_RESCHEDULE_PROPOSED)

        self._booking_settings = None
        self._site_settings = None

    def build_engine_request(
        self,
        service_ids: list[int],
        target_date: date,
        mode: BookingMode = BookingMode.SINGLE_DAY,
        locked_master_id: int | None = None,
        master_selections: dict[str, str] | None = None,
    ) -> BookingEngineRequest:
        services = self.service_model.objects.filter(id__in=service_ids).select_related("category")
        service_map = {s.id: s for s in services}

        weekday = target_date.weekday()
        service_requests = []

        for idx, svc_id in enumerate(service_ids):
            service = service_map.get(svc_id)
            if not service:
                continue

            if locked_master_id:
                possible_ids = [str(locked_master_id)]
            elif master_selections and str(idx) in master_selections:
                m_id = master_selections[str(idx)]
                if m_id == "any":
                    masters = self.master_model.objects.filter(
                        categories=service.category, status=self.master_model.STATUS_ACTIVE
                    )
                    possible_ids = [str(m.pk) for m in masters if weekday in (m.work_days or [])]
                else:
                    possible_ids = [str(m_id)]
            else:
                masters = self.master_model.objects.filter(
                    categories=service.category,
                    status=self.master_model.STATUS_ACTIVE,
                )
                possible_ids = [str(m.pk) for m in masters if weekday in (m.work_days or [])]

            if not possible_ids:
                continue

            gap = getattr(service, "min_gap_after_minutes", 0) or 0
            service_requests.append(
                ServiceRequest(
                    service_id=str(svc_id),
                    duration_minutes=service.duration,
                    min_gap_after_minutes=gap,
                    possible_master_ids=possible_ids,
                )
            )

        return BookingEngineRequest(
            service_requests=service_requests,
            booking_date=target_date,
            mode=mode,
        )

    def build_masters_availability(
        self,
        master_ids: list[int],
        target_date: date,
        cache_ttl: int = 0,
        exclude_appointment_ids: list[int] | None = None,
    ) -> dict[str, MasterAvailability]:
        cache_key = None
        if cache_ttl > 0 and not exclude_appointment_ids:
            sorted_ids = ",".join(str(i) for i in sorted(master_ids))
            cache_key = f"booking_avail:{target_date}:{sorted_ids}"
            cached = cache.get(cache_key)
            if cached is not None:
                return cached  # type: ignore[no-any-return]

        settings = self._get_booking_settings()
        result: dict[str, MasterAvailability] = {}

        day_off_ids = set(
            self.day_off_model.objects.filter(master_id__in=master_ids, date=target_date).values_list(
                "master_id", flat=True
            )
        )

        appt_filter = {
            "master_id__in": master_ids,
            "datetime_start__date": target_date,
            "status__in": self.appointment_status_filter,
        }
        appointments_qs = self.appointment_model.objects.filter(**appt_filter)
        if exclude_appointment_ids:
            appointments_qs = appointments_qs.exclude(id__in=exclude_appointment_ids)
        appointments = appointments_qs.order_by("datetime_start")

        busy_by_master: dict[int, list[tuple[datetime, datetime]]] = {mid: [] for mid in master_ids}
        for app in appointments:
            s = app.datetime_start.astimezone(UTC).replace(second=0, microsecond=0)
            e = s + timedelta(minutes=app.duration_minutes)
            busy_by_master[app.master_id].append((s, e))

        masters = self.master_model.objects.filter(pk__in=master_ids)
        for master in masters:
            if master.pk in day_off_ids:
                continue

            working_hours_utc = self.get_master_working_hours(master, target_date)
            if not working_hours_utc:
                continue

            work_start_dt, work_end_dt = working_hours_utc
            break_interval = self.get_break_interval(master, target_date)
            buffer = self.get_buffer_minutes(master, settings)

            free_windows = self._calc.merge_free_windows(
                work_start=work_start_dt,
                work_end=work_end_dt,
                busy_intervals=busy_by_master.get(master.pk, []),
                break_interval=break_interval,
                buffer_minutes=buffer,
                min_duration_minutes=self.step_minutes,
            )

            result[str(master.pk)] = MasterAvailability(
                master_id=str(master.pk),
                free_windows=free_windows,
                buffer_between_minutes=buffer,
            )

        if cache_ttl > 0 and cache_key:
            cache.set(cache_key, result, timeout=cache_ttl)

        return result

    def lock_masters(self, master_ids: list[int]) -> None:
        if not master_ids:
            return
        sorted_ids = sorted(master_ids)
        list(self.master_model.objects.select_for_update().filter(pk__in=sorted_ids))

    def result_to_slots_map(self, result: EngineResult) -> dict[str, bool]:
        times = result.get_unique_start_times()
        return dict.fromkeys(times, True)

    def get_work_start(self, master: Any) -> Any:
        return getattr(master, "work_start", None)

    def get_work_end(self, master: Any) -> Any:
        return getattr(master, "work_end", None)

    def get_break_start(self, master: Any) -> Any:
        return getattr(master, "break_start", None)

    def get_break_end(self, master: Any) -> Any:
        return getattr(master, "break_end", None)

    def get_master_timezone(self, master: Any) -> str:
        tz = getattr(master, "timezone", None)
        if tz:
            return tz  # type: ignore[no-any-return]
        site = self._get_site_settings()
        return getattr(site, "timezone", None) or "UTC"

    def get_buffer_minutes(self, master: Any, settings: Any) -> int:
        individual = getattr(master, "buffer_between_minutes", None)
        if individual is not None:
            return individual  # type: ignore[no-any-return]
        return settings.default_buffer_between_minutes  # type: ignore[no-any-return]

    def get_master_working_hours(self, master: Any, target_date: date) -> tuple[datetime, datetime] | None:
        weekday = target_date.weekday()
        if master.work_days and weekday not in master.work_days:
            return None

        tz_name = self.get_master_timezone(master)
        try:
            tz = zoneinfo.ZoneInfo(tz_name)
        except Exception:
            tz = zoneinfo.ZoneInfo("UTC")

        start_t = self.get_work_start(master)
        end_t = self.get_work_end(master)

        if not (start_t and end_t):
            site = self._get_site_settings()
            if weekday < 5:
                start_t, end_t = site.work_start_weekdays, site.work_end_weekdays
            elif weekday == 5:
                start_t, end_t = site.work_start_saturday, site.work_end_saturday

        if not start_t or not end_t:
            return None

        work_start_dt = datetime.combine(target_date, start_t, tzinfo=tz)
        work_end_dt = datetime.combine(target_date, end_t, tzinfo=tz)
        return (work_start_dt.astimezone(UTC), work_end_dt.astimezone(UTC))

    def get_break_interval(self, master: Any, target_date: date) -> tuple[datetime, datetime] | None:
        break_start = self.get_break_start(master)
        break_end = self.get_break_end(master)

        if break_start and break_end:
            tz_name = self.get_master_timezone(master)
            try:
                tz = zoneinfo.ZoneInfo(tz_name)
            except Exception:
                tz = zoneinfo.ZoneInfo("UTC")

            bs = datetime.combine(target_date, break_start, tzinfo=tz)
            be = datetime.combine(target_date, break_end, tzinfo=tz)
            return (bs.astimezone(UTC), be.astimezone(UTC))

        return None

    def _get_booking_settings(self) -> Any:
        if self._booking_settings is None:
            self._booking_settings = self.booking_settings_model.load()
        return self._booking_settings

    def _get_site_settings(self) -> Any:
        if self._site_settings is None:
            self._site_settings = self.site_settings_model.load()
        return self._site_settings
