"""Unit tests for DjangoAvailabilityAdapter."""

from datetime import UTC, date, datetime, time, timedelta
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture
def adapter(adapter_models):
    from codex_django.booking.adapters.availability import DjangoAvailabilityAdapter

    cache = MagicMock()
    cache.get_busy.return_value = None
    with patch("codex_django.booking.adapters.availability.SlotCalculator"):
        return DjangoAvailabilityAdapter(
            resource_model=adapter_models["master"],
            appointment_model=adapter_models["appointment"],
            service_model=adapter_models["service"],
            working_day_model=adapter_models["working_day"],
            day_off_model=adapter_models["day_off"],
            booking_settings_model=adapter_models["booking_settings"],
            site_settings_model=adapter_models["site_settings"],
            step_minutes=30,
            cache_adapter=cache,
        )


# ---------------------------------------------------------------------------
# __init__ / construction
# ---------------------------------------------------------------------------


class TestDjangoAvailabilityAdapterInit:
    def test_step_minutes_stored(self, adapter):
        assert adapter.step_minutes == 30

    def test_status_filter_default_includes_pending_and_confirmed(self, adapter_models):
        from codex_django.booking.adapters.availability import DjangoAvailabilityAdapter

        adapter_models["appointment"].STATUS_PENDING = "pending"
        adapter_models["appointment"].STATUS_CONFIRMED = "confirmed"
        with patch("codex_django.booking.adapters.availability.SlotCalculator"):
            a = DjangoAvailabilityAdapter(
                resource_model=adapter_models["master"],
                appointment_model=adapter_models["appointment"],
                service_model=adapter_models["service"],
                working_day_model=adapter_models["working_day"],
                day_off_model=adapter_models["day_off"],
                booking_settings_model=adapter_models["booking_settings"],
                site_settings_model=adapter_models["site_settings"],
                step_minutes=30,
            )
        assert "pending" in a.appointment_status_filter
        assert "confirmed" in a.appointment_status_filter

    def test_status_filter_includes_reschedule_if_present(self, adapter_models):
        from codex_django.booking.adapters.availability import DjangoAvailabilityAdapter

        adapter_models["appointment"].STATUS_RESCHEDULE_PROPOSED = "reschedule_proposed"
        with patch("codex_django.booking.adapters.availability.SlotCalculator"):
            a = DjangoAvailabilityAdapter(
                resource_model=adapter_models["master"],
                appointment_model=adapter_models["appointment"],
                service_model=adapter_models["service"],
                working_day_model=adapter_models["working_day"],
                day_off_model=adapter_models["day_off"],
                booking_settings_model=adapter_models["booking_settings"],
                site_settings_model=adapter_models["site_settings"],
                step_minutes=30,
            )
        assert "reschedule_proposed" in a.appointment_status_filter

    def test_custom_status_filter_respected(self, adapter_models):
        from codex_django.booking.adapters.availability import DjangoAvailabilityAdapter

        with patch("codex_django.booking.adapters.availability.SlotCalculator"):
            a = DjangoAvailabilityAdapter(
                resource_model=adapter_models["master"],
                appointment_model=adapter_models["appointment"],
                service_model=adapter_models["service"],
                working_day_model=adapter_models["working_day"],
                day_off_model=adapter_models["day_off"],
                booking_settings_model=adapter_models["booking_settings"],
                site_settings_model=adapter_models["site_settings"],
                appointment_status_filter=["done"],
            )
        assert a.appointment_status_filter == ["done"]

    def test_default_cache_adapter_created_when_not_provided(self, adapter_models):
        from codex_django.booking.adapters.availability import DjangoAvailabilityAdapter

        with (
            patch("codex_django.booking.adapters.availability.SlotCalculator"),
            patch("codex_django.booking.adapters.availability.BookingCacheAdapter") as mock_cls,
        ):
            mock_cls.return_value = MagicMock()
            DjangoAvailabilityAdapter(
                resource_model=adapter_models["master"],
                appointment_model=adapter_models["appointment"],
                service_model=adapter_models["service"],
                working_day_model=adapter_models["working_day"],
                day_off_model=adapter_models["day_off"],
                booking_settings_model=adapter_models["booking_settings"],
                site_settings_model=adapter_models["site_settings"],
            )
            mock_cls.assert_called_once()


# ---------------------------------------------------------------------------
# _resolve_resource_ids
# ---------------------------------------------------------------------------


class TestResolveResourceIds:
    def test_returns_locked_resource_id_when_provided(self, adapter):
        result = adapter._resolve_resource_ids(
            service=MagicMock(),
            weekday=0,
            locked_resource_id=99,
            resource_selections=None,
            service_id=5,
        )
        assert result == ["99"]

    def test_returns_selection_from_resource_selections(self, adapter):
        result = adapter._resolve_resource_ids(
            service=MagicMock(),
            weekday=0,
            locked_resource_id=None,
            resource_selections={5: 7},
            service_id=5,
        )
        assert result == ["7"]

    def test_ignores_any_selection_and_queries_db(self, adapter, adapter_models):
        # "any" means fall through to DB
        m1 = MagicMock()
        m1.pk = 1
        masters_qs = MagicMock()
        masters_qs.__iter__ = MagicMock(return_value=iter([m1]))
        masters_qs.values_list.return_value = [1]
        adapter_models["master"].objects.filter.return_value = masters_qs
        adapter_models["working_day"].objects.filter.return_value.values_list.return_value = [1]

        result = adapter._resolve_resource_ids(
            service=MagicMock(),
            weekday=0,
            locked_resource_id=None,
            resource_selections={5: None},
            service_id=5,
        )
        # Should return master IDs from DB, not ["any"]
        assert result == ["1"]

    def test_locked_resource_id_takes_priority_over_selections(self, adapter):
        result = adapter._resolve_resource_ids(
            service=MagicMock(),
            weekday=0,
            locked_resource_id=5,
            resource_selections={7: 7},
            service_id=7,
        )
        assert result == ["5"]

    def test_empty_list_when_no_masters_with_schedule(self, adapter, adapter_models):
        masters_qs = MagicMock()
        masters_qs.__iter__ = MagicMock(return_value=iter([]))
        masters_qs.values_list.return_value = []
        adapter_models["master"].objects.filter.return_value = masters_qs
        adapter_models["working_day"].objects.filter.return_value.values_list.return_value = []

        result = adapter._resolve_resource_ids(
            service=MagicMock(),
            weekday=0,
            locked_resource_id=None,
            resource_selections=None,
            service_id=5,
        )
        assert result == []


# ---------------------------------------------------------------------------
# _normalize_resource_selections
# ---------------------------------------------------------------------------


class TestNormalizeResourceSelections:
    def test_returns_empty_for_none(self, adapter):
        assert adapter._normalize_resource_selections([5, 7], None) == {}

    def test_normalizes_legacy_positional_format(self, adapter):
        result = adapter._normalize_resource_selections([5, 7], {"0": "10", "1": "12"})
        assert result == {5: 10, 7: 12}

    def test_legacy_any_is_ignored(self, adapter):
        result = adapter._normalize_resource_selections([5, 7], {"0": "10", "1": "any"})
        assert result == {5: 10}

    def test_new_format_int_keys(self, adapter):
        result = adapter._normalize_resource_selections([5, 7], {5: 10, 7: None})
        assert result == {5: 10, 7: None}

    def test_new_format_str_keys(self, adapter):
        result = adapter._normalize_resource_selections([5, 7], {"5": "10", "7": "12"})
        assert result == {5: 10, 7: 12}


# ---------------------------------------------------------------------------
# get_working_hours
# ---------------------------------------------------------------------------


class TestGetWorkingHours:
    def _master(self, tz="UTC", work_start=None, work_end=None):
        m = MagicMock()
        m.pk = 1
        m.timezone = tz
        m.work_start = work_start
        m.work_end = work_end
        return m

    def test_uses_working_day_model_when_present(self, adapter, adapter_models):
        wd = MagicMock()
        wd.start_time = time(9, 0)
        wd.end_time = time(17, 0)
        adapter_models["working_day"].objects.filter.return_value.first.return_value = wd
        master = self._master(tz="UTC")
        result = adapter.get_working_hours(master, date(2025, 1, 6))
        assert result is not None
        start_utc, end_utc = result
        assert start_utc.hour == 9
        assert end_utc.hour == 17

    def test_falls_back_to_master_defaults(self, adapter, adapter_models):
        adapter_models["working_day"].objects.filter.return_value.first.return_value = None
        master = self._master(tz="UTC", work_start=time(10, 0), work_end=time(18, 0))
        result = adapter.get_working_hours(master, date(2025, 1, 6))
        assert result is not None
        start_utc, end_utc = result
        assert start_utc.hour == 10
        assert end_utc.hour == 18

    def test_falls_back_to_site_settings_weekday(self, adapter, adapter_models):
        adapter_models["working_day"].objects.filter.return_value.first.return_value = None
        site = MagicMock()
        site.work_start_weekdays = time(8, 0)
        site.work_end_weekdays = time(16, 0)
        site.timezone = "UTC"
        adapter_models["site_settings"].objects.first.return_value = site
        master = self._master(tz="UTC", work_start=None, work_end=None)
        result = adapter.get_working_hours(master, date(2025, 1, 6))  # Monday
        assert result is not None
        start_utc, _ = result
        assert start_utc.hour == 8

    def test_returns_none_when_nothing_configured(self, adapter, adapter_models):
        adapter_models["working_day"].objects.filter.return_value.first.return_value = None
        site = MagicMock()
        site.work_start_weekdays = None
        site.work_end_weekdays = None
        site.work_start_saturday = None
        site.work_end_saturday = None
        site.timezone = "UTC"
        adapter_models["site_settings"].objects.first.return_value = site
        master = self._master(tz="UTC", work_start=None, work_end=None)
        result = adapter.get_working_hours(master, date(2025, 1, 6))
        assert result is None

    def test_converts_local_time_to_utc(self, adapter, adapter_models):
        """Berlin UTC+1 in winter: 09:00 local → 08:00 UTC."""
        wd = MagicMock()
        wd.start_time = time(9, 0)
        wd.end_time = time(17, 0)
        adapter_models["working_day"].objects.filter.return_value.first.return_value = wd
        master = self._master(tz="Europe/Berlin")
        result = adapter.get_working_hours(master, date(2025, 1, 6))
        assert result is not None
        start_utc, _ = result
        assert start_utc.hour == 8  # 09:00 CET = 08:00 UTC

    def test_result_is_utc_aware(self, adapter, adapter_models):
        wd = MagicMock()
        wd.start_time = time(9, 0)
        wd.end_time = time(17, 0)
        adapter_models["working_day"].objects.filter.return_value.first.return_value = wd
        master = self._master(tz="UTC")
        start_utc, end_utc = adapter.get_working_hours(master, date(2025, 1, 6))
        assert start_utc.tzinfo is UTC
        assert end_utc.tzinfo is UTC


# ---------------------------------------------------------------------------
# get_break_interval
# ---------------------------------------------------------------------------


class TestGetBreakInterval:
    def _master(self, tz="UTC", break_start=None, break_end=None):
        m = MagicMock()
        m.pk = 1
        m.timezone = tz
        m.break_start = break_start
        m.break_end = break_end
        return m

    def test_returns_break_from_working_day(self, adapter, adapter_models):
        wd = MagicMock()
        wd.break_start = time(12, 0)
        wd.break_end = time(13, 0)
        adapter_models["working_day"].objects.filter.return_value.first.return_value = wd
        master = self._master(tz="UTC")
        result = adapter.get_break_interval(master, date(2025, 1, 6))
        assert result is not None
        bs, be = result
        assert bs.hour == 12
        assert be.hour == 13

    def test_falls_back_to_master_break(self, adapter, adapter_models):
        # working_day returns None → fall back to master attributes
        adapter_models["working_day"].objects.filter.return_value.first.return_value = None
        master = self._master(tz="UTC", break_start=time(12, 0), break_end=time(12, 30))
        result = adapter.get_break_interval(master, date(2025, 1, 6))
        assert result is not None
        bs, _ = result
        assert bs.hour == 12

    def test_returns_none_when_working_day_has_no_break(self, adapter, adapter_models):
        # working_day exists but break_start/break_end are None
        wd = MagicMock()
        wd.break_start = None
        wd.break_end = None
        adapter_models["working_day"].objects.filter.return_value.first.return_value = wd
        master = self._master(tz="UTC")
        assert adapter.get_break_interval(master, date(2025, 1, 6)) is None

    def test_returns_none_when_no_working_day_and_no_master_break(self, adapter, adapter_models):
        adapter_models["working_day"].objects.filter.return_value.first.return_value = None
        master = self._master(tz="UTC", break_start=None, break_end=None)
        assert adapter.get_break_interval(master, date(2025, 1, 6)) is None


# ---------------------------------------------------------------------------
# _get_busy_intervals
# ---------------------------------------------------------------------------


class TestGetBusyIntervals:
    def _make_appointment(self, resource_id, start_dt, duration_minutes):
        appt = MagicMock()
        appt.master_id = resource_id
        appt.datetime_start = start_dt
        appt.duration_minutes = duration_minutes
        return appt

    def test_builds_dict_keyed_by_master_id(self, adapter, adapter_models):
        appt = self._make_appointment(
            resource_id=1,
            start_dt=datetime(2025, 1, 6, 9, 0, tzinfo=UTC),
            duration_minutes=60,
        )
        qs = MagicMock()
        qs.__iter__ = MagicMock(return_value=iter([appt]))
        adapter_models["appointment"].objects.filter.return_value.order_by.return_value = qs
        result = adapter._get_busy_intervals([1], date(2025, 1, 6))
        assert 1 in result
        assert len(result[1]) == 1
        start, end = result[1][0]
        assert end - start == timedelta(minutes=60)

    def test_empty_list_for_master_with_no_appointments(self, adapter, adapter_models):
        qs = MagicMock()
        qs.__iter__ = MagicMock(return_value=iter([]))
        adapter_models["appointment"].objects.filter.return_value.order_by.return_value = qs
        result = adapter._get_busy_intervals([1, 2], date(2025, 1, 6))
        assert result == {1: [], 2: []}

    def test_excludes_appointment_ids(self, adapter, adapter_models):
        qs = MagicMock()
        qs.__iter__ = MagicMock(return_value=iter([]))
        exclude_qs = MagicMock()
        exclude_qs.order_by.return_value = qs
        filter_qs = MagicMock()
        filter_qs.exclude.return_value = exclude_qs
        adapter_models["appointment"].objects.filter.return_value = filter_qs
        adapter._get_busy_intervals([1], date(2025, 1, 6), exclude_appointment_ids=[5, 6])
        filter_qs.exclude.assert_called_once_with(id__in=[5, 6])

    def test_intervals_are_utc_with_seconds_stripped(self, adapter, adapter_models):
        appt = self._make_appointment(
            resource_id=1,
            start_dt=datetime(2025, 1, 6, 9, 30, 45, tzinfo=UTC),
            duration_minutes=30,
        )
        qs = MagicMock()
        qs.__iter__ = MagicMock(return_value=iter([appt]))
        adapter_models["appointment"].objects.filter.return_value.order_by.return_value = qs
        result = adapter._get_busy_intervals([1], date(2025, 1, 6))
        s, _ = result[1][0]
        assert s.second == 0
        assert s.microsecond == 0

    def test_multiple_appointments_same_master(self, adapter, adapter_models):
        appt1 = self._make_appointment(1, datetime(2025, 1, 6, 9, 0, tzinfo=UTC), 30)
        appt2 = self._make_appointment(1, datetime(2025, 1, 6, 11, 0, tzinfo=UTC), 60)
        qs = MagicMock()
        qs.__iter__ = MagicMock(return_value=iter([appt1, appt2]))
        adapter_models["appointment"].objects.filter.return_value.order_by.return_value = qs
        result = adapter._get_busy_intervals([1], date(2025, 1, 6))
        assert len(result[1]) == 2


# ---------------------------------------------------------------------------
# result_to_slots_map
# ---------------------------------------------------------------------------


class TestResultToSlotsMap:
    def test_empty_result_gives_empty_dict(self, adapter):
        mock_result = MagicMock()
        mock_result.get_unique_start_times.return_value = []
        assert adapter.result_to_slots_map(mock_result) == {}

    def test_returns_dict_with_true_values(self, adapter):
        mock_result = MagicMock()
        mock_result.get_unique_start_times.return_value = ["09:00", "09:30", "10:00"]
        result = adapter.result_to_slots_map(mock_result)
        assert result == {"09:00": True, "09:30": True, "10:00": True}

    def test_all_values_are_true(self, adapter):
        mock_result = MagicMock()
        mock_result.get_unique_start_times.return_value = ["09:00", "10:00"]
        result = adapter.result_to_slots_map(mock_result)
        assert all(v is True for v in result.values())


# ---------------------------------------------------------------------------
# lock_resources
# ---------------------------------------------------------------------------


class TestLockMasters:
    def test_noop_when_empty_list(self, adapter, adapter_models):
        adapter.lock_resources([])
        adapter_models["master"].objects.select_for_update.assert_not_called()

    def test_sorts_ids_before_locking(self, adapter, adapter_models):
        only_qs = MagicMock()
        only_qs.__iter__ = MagicMock(return_value=iter([]))
        filter_qs = MagicMock()
        filter_qs.only.return_value = only_qs
        sfu_qs = MagicMock()
        sfu_qs.filter.return_value = filter_qs
        adapter_models["master"].objects.select_for_update.return_value = sfu_qs
        adapter.lock_resources([3, 1, 2])
        filter_call_kwargs = sfu_qs.filter.call_args[1]
        assert filter_call_kwargs["pk__in"] == [1, 2, 3]

    def test_uses_select_for_update_with_of_self(self, adapter, adapter_models):
        only_qs = MagicMock()
        only_qs.__iter__ = MagicMock(return_value=iter([]))
        filter_qs = MagicMock()
        filter_qs.only.return_value = only_qs
        sfu_qs = MagicMock()
        sfu_qs.filter.return_value = filter_qs
        adapter_models["master"].objects.select_for_update.return_value = sfu_qs
        adapter.lock_resources([1])
        adapter_models["master"].objects.select_for_update.assert_called_once_with(of=("self",))


# ---------------------------------------------------------------------------
# _get_buffer_minutes
# ---------------------------------------------------------------------------


class TestGetBufferMinutes:
    def test_uses_master_buffer_when_set(self, adapter):
        master = MagicMock()
        master.buffer_between_minutes = 15
        settings = MagicMock()
        settings.default_buffer_between_minutes = 5
        assert adapter._get_buffer_minutes(master, settings) == 15

    def test_falls_back_to_settings_when_master_has_none(self, adapter):
        master = MagicMock()
        master.buffer_between_minutes = None
        settings = MagicMock()
        settings.default_buffer_between_minutes = 10
        assert adapter._get_buffer_minutes(master, settings) == 10

    def test_zero_buffer_from_master_is_used(self, adapter):
        master = MagicMock()
        master.buffer_between_minutes = 0
        settings = MagicMock()
        settings.default_buffer_between_minutes = 10
        # 0 is falsy but not None — should use master's 0
        assert adapter._get_buffer_minutes(master, settings) == 0


# ---------------------------------------------------------------------------
# _get_tz
# ---------------------------------------------------------------------------


class TestGetTz:
    def test_uses_master_timezone(self, adapter):
        master = MagicMock()
        master.timezone = "Europe/Berlin"
        tz = adapter._get_tz(master)
        assert str(tz) == "Europe/Berlin"

    def test_returns_utc_for_invalid_tz(self, adapter, adapter_models):
        site = MagicMock()
        site.timezone = None
        adapter_models["site_settings"].objects.first.return_value = site
        master = MagicMock()
        master.timezone = "Invalid/Zone"
        tz = adapter._get_tz(master)
        assert str(tz) == "UTC"

    def test_falls_back_to_utc_when_no_tz_anywhere(self, adapter, adapter_models):
        site = MagicMock()
        site.timezone = None
        adapter_models["site_settings"].objects.first.return_value = site
        master = MagicMock()
        master.timezone = None
        tz = adapter._get_tz(master)
        assert str(tz) == "UTC"


# ---------------------------------------------------------------------------
# build_engine_request
# ---------------------------------------------------------------------------


class TestBuildEngineRequest:
    def test_returns_service_requests(self, adapter, adapter_models):
        service = MagicMock()
        service.id = 5
        service.duration = 60
        service.min_gap_after_minutes = 0
        service.parallel_group = None
        adapter_models["service"].objects.filter.return_value.select_related.return_value = [service]

        with patch.object(adapter, "_resolve_resource_ids", return_value=["1", "2"]):
            result = adapter.build_engine_request(service_ids=[5], target_date=date(2025, 1, 6))
        assert len(result.service_requests) == 1
        sr = result.service_requests[0]
        assert sr.service_id == "5"
        assert sr.duration_minutes == 60
        assert sr.possible_resource_ids == ["1", "2"]

    def test_skips_service_not_in_db_raises_validation(self, adapter, adapter_models):
        """BookingEngineRequest requires >=1 service_request; missing service → ValidationError."""
        from pydantic import ValidationError

        adapter_models["service"].objects.filter.return_value.select_related.return_value = []
        with pytest.raises(ValidationError):
            adapter.build_engine_request(service_ids=[999], target_date=date(2025, 1, 6))

    def test_skips_service_with_no_masters_raises_validation(self, adapter, adapter_models):
        """If _resolve_resource_ids returns [] for all services → ValidationError."""
        from pydantic import ValidationError

        service = MagicMock()
        service.id = 5
        service.duration = 60
        adapter_models["service"].objects.filter.return_value.select_related.return_value = [service]
        with (
            patch.object(adapter, "_resolve_resource_ids", return_value=[]),
            pytest.raises(ValidationError),
        ):
            adapter.build_engine_request(service_ids=[5], target_date=date(2025, 1, 6))

    def test_booking_date_on_request(self, adapter, adapter_models):
        service = MagicMock()
        service.id = 5
        service.duration = 60
        service.min_gap_after_minutes = 0
        service.parallel_group = None
        adapter_models["service"].objects.filter.return_value.select_related.return_value = [service]
        with patch.object(adapter, "_resolve_resource_ids", return_value=["1"]):
            result = adapter.build_engine_request(service_ids=[5], target_date=date(2025, 3, 15))
        assert result.booking_date == date(2025, 3, 15)

    def test_multiple_services(self, adapter, adapter_models):
        svc1 = MagicMock()
        svc1.id = 1
        svc1.duration = 30
        svc1.min_gap_after_minutes = 0
        svc1.parallel_group = None
        svc2 = MagicMock()
        svc2.id = 2
        svc2.duration = 60
        svc2.min_gap_after_minutes = 5
        svc2.parallel_group = None
        adapter_models["service"].objects.filter.return_value.select_related.return_value = [svc1, svc2]
        with patch.object(adapter, "_resolve_resource_ids", return_value=["1"]):
            result = adapter.build_engine_request(service_ids=[1, 2], target_date=date(2025, 1, 6))
        assert len(result.service_requests) == 2

    def test_passes_mode_to_booking_engine_request(self, adapter, adapter_models):
        from codex_services.booking.slot_master.modes import BookingMode

        service = MagicMock()
        service.id = 5
        service.duration = 60
        service.min_gap_after_minutes = 0
        service.parallel_group = None
        adapter_models["service"].objects.filter.return_value.select_related.return_value = [service]

        with patch.object(adapter, "_resolve_resource_ids", return_value=["10"]):
            result = adapter.build_engine_request(
                service_ids=[5],
                target_date=date(2026, 4, 1),
                mode=BookingMode.MULTI_DAY,
            )

        assert result.mode == BookingMode.MULTI_DAY

    def test_passes_overlap_allowed_to_booking_engine_request(self, adapter, adapter_models):
        service = MagicMock()
        service.id = 5
        service.duration = 60
        service.min_gap_after_minutes = 0
        service.parallel_group = None
        adapter_models["service"].objects.filter.return_value.select_related.return_value = [service]

        with patch.object(adapter, "_resolve_resource_ids", return_value=["10"]):
            result = adapter.build_engine_request(
                service_ids=[5],
                target_date=date(2026, 4, 1),
                overlap_allowed=True,
            )

        assert result.overlap_allowed is True

    def test_new_resource_selections_format_is_service_keyed(self, adapter, adapter_models):
        svc1 = MagicMock()
        svc1.id = 5
        svc1.duration = 30
        svc1.min_gap_after_minutes = 0
        svc1.parallel_group = None
        svc2 = MagicMock()
        svc2.id = 7
        svc2.duration = 60
        svc2.min_gap_after_minutes = 0
        svc2.parallel_group = None
        adapter_models["service"].objects.filter.return_value.select_related.return_value = [svc1, svc2]

        with patch.object(
            adapter,
            "_resolve_resource_ids",
            side_effect=[["10"], ["12"]],
        ) as mock_resolve:
            result = adapter.build_engine_request(
                service_ids=[5, 7],
                target_date=date(2026, 4, 1),
                resource_selections={5: 10, 7: 12},
            )

        assert len(result.service_requests) == 2
        assert result.service_requests[0].possible_resource_ids == ["10"]
        assert result.service_requests[1].possible_resource_ids == ["12"]
        assert mock_resolve.call_args_list[0].kwargs["service_id"] == 5
        assert mock_resolve.call_args_list[1].kwargs["service_id"] == 7
        assert mock_resolve.call_args_list[0].kwargs["resource_selections"] == {5: 10, 7: 12}

    def test_legacy_resource_selections_still_supported(self, adapter, adapter_models):
        svc1 = MagicMock()
        svc1.id = 5
        svc1.duration = 30
        svc1.min_gap_after_minutes = 0
        svc1.parallel_group = None
        svc2 = MagicMock()
        svc2.id = 7
        svc2.duration = 60
        svc2.min_gap_after_minutes = 0
        svc2.parallel_group = None
        adapter_models["service"].objects.filter.return_value.select_related.return_value = [svc1, svc2]

        with patch.object(
            adapter,
            "_resolve_resource_ids",
            side_effect=[["10"], ["12"]],
        ) as mock_resolve:
            adapter.build_engine_request(
                service_ids=[5, 7],
                target_date=date(2026, 4, 1),
                resource_selections={"0": "10", "1": "12"},
            )

        assert mock_resolve.call_args_list[0].kwargs["resource_selections"] == {5: 10, 7: 12}

    def test_missing_service_in_selection_means_any(self, adapter, adapter_models):
        svc1 = MagicMock()
        svc1.id = 5
        svc1.duration = 30
        svc1.min_gap_after_minutes = 0
        svc1.parallel_group = None
        svc2 = MagicMock()
        svc2.id = 7
        svc2.duration = 60
        svc2.min_gap_after_minutes = 0
        svc2.parallel_group = None
        adapter_models["service"].objects.filter.return_value.select_related.return_value = [svc1, svc2]

        with patch.object(adapter, "_resolve_resource_ids", side_effect=[["10"], ["12", "13"]]) as mock_resolve:
            result = adapter.build_engine_request(
                service_ids=[5, 7],
                target_date=date(2026, 4, 1),
                resource_selections={5: 10},
            )

        assert len(result.service_requests) == 2
        assert mock_resolve.call_args_list[1].kwargs["resource_selections"] == {5: 10}

    def test_parallel_groups_override_service_field(self, adapter, adapter_models):
        svc1 = MagicMock()
        svc1.id = 5
        svc1.duration = 30
        svc1.min_gap_after_minutes = 0
        svc1.parallel_group = "from_model"
        svc2 = MagicMock()
        svc2.id = 7
        svc2.duration = 60
        svc2.min_gap_after_minutes = 0
        svc2.parallel_group = None
        adapter_models["service"].objects.filter.return_value.select_related.return_value = [svc1, svc2]

        with patch.object(adapter, "_resolve_resource_ids", return_value=["10"]):
            result = adapter.build_engine_request(
                service_ids=[5, 7],
                target_date=date(2026, 4, 1),
                parallel_groups={5: "A", 7: "B"},
            )

        assert result.service_requests[0].parallel_group == "A"
        assert result.service_requests[1].parallel_group == "B"

    def test_calls_prioritize_resource_ids_seam(self, adapter, adapter_models):
        service = MagicMock()
        service.id = 5
        service.duration = 60
        service.min_gap_after_minutes = 0
        service.parallel_group = None
        adapter_models["service"].objects.filter.return_value.select_related.return_value = [service]

        with (
            patch.object(adapter, "_resolve_resource_ids", return_value=["10", "11"]),
            patch.object(adapter, "prioritize_resource_ids", return_value=["11", "10"]) as prioritize_mock,
        ):
            result = adapter.build_engine_request(service_ids=[5], target_date=date(2026, 4, 1))

        assert result.service_requests[0].possible_resource_ids == ["11", "10"]
        prioritize_mock.assert_called_once()
