from datetime import date, time
from unittest.mock import MagicMock

import pytest

from codex_django.booking.adapters.availability import DjangoAvailabilityAdapter


@pytest.fixture
def adapter():
    master_model = MagicMock()
    master_model.STATUS_ACTIVE = "active"
    return DjangoAvailabilityAdapter(
        master_model=master_model,
        appointment_model=MagicMock(),
        service_model=MagicMock(),
        working_day_model=MagicMock(),
        day_off_model=MagicMock(),
        booking_settings_model=MagicMock(),
        site_settings_model=MagicMock(),
    )


@pytest.mark.unit
def test_get_working_hours_site_defaults(adapter, settings):
    settings.BASE_DIR = "."
    adapter.working_day_model.objects.filter.return_value.first.return_value = None
    adapter.site_settings_model.objects.first.return_value = MagicMock(
        work_start_weekdays=time(9, 0),
        work_end_weekdays=time(18, 0),
        work_start_saturday=time(10, 0),
        work_end_saturday=time(16, 0),
        timezone="UTC",
    )

    master = MagicMock(pk=1)
    master.work_start = None
    master.work_end = None
    master.timezone = "UTC"

    # Monday
    res = adapter.get_working_hours(master, date(2024, 1, 1))
    assert res[0].hour == 9

    # Saturday
    res = adapter.get_working_hours(master, date(2024, 1, 6))
    assert res[0].hour == 10


@pytest.mark.unit
def test_build_masters_availability(adapter):
    master = MagicMock(pk=1)
    # Ensure buffer and timezone are real values to avoid TypeError in timedelta
    master.buffer_between_minutes = 0
    master.timezone = "UTC"

    adapter.master_model.objects.filter.return_value = [master]
    adapter.day_off_model.objects.filter.return_value.values_list.return_value = []

    # Mock working hours
    adapter.working_day_model.objects.filter.return_value.first.return_value = MagicMock(
        start_time=time(9, 0), end_time=time(17, 0), break_start=time(13, 0), break_end=time(14, 0)
    )

    adapter.booking_settings_model.objects.first.return_value = MagicMock(default_buffer_between_minutes=0)

    res = adapter.build_masters_availability([1], date(2024, 1, 1))
    assert "1" in res
    assert len(res["1"].free_windows) > 0


@pytest.mark.unit
def test_normalize_master_selections_edge_cases(adapter):
    # Pass real int value instead of MagicMock to satisfy isinstance(raw_val, (str, int))
    res = adapter._normalize_master_selections([10], {10: 5})
    assert 10 in res
    assert res[10] == 5

    # Test legacy positional
    res = adapter._normalize_master_selections([100, 200], {"0": "10", "1": "20"})
    assert res[100] == 10
    assert res[200] == 20
