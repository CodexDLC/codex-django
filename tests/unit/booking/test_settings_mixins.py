from __future__ import annotations

from datetime import time
from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from codex_django.booking.mixins.settings import AbstractBookingSettings, BookingSettingsMixin, BookingSettingsSyncMixin

pytestmark = pytest.mark.unit


class ConcreteBookingSettings(BookingSettingsMixin):
    class Meta:
        app_label = "tests"


class ConcreteBookingSettingsSync(BookingSettingsSyncMixin):
    class Meta:
        app_label = "tests"


class ConcreteBookingSettingsSyncNoDict(BookingSettingsSyncMixin):
    class Meta:
        app_label = "tests"


class ConcreteAbstractBookingSettings(AbstractBookingSettings):
    class Meta:
        app_label = "tests"


def test_booking_settings_to_dict_serializes_concrete_fields():
    settings = ConcreteBookingSettings(
        step_minutes=15,
        default_buffer_between_minutes=5,
        min_advance_minutes=30,
        max_advance_days=14,
        monday_is_closed=False,
        work_start_monday=time(9, 0),
        work_end_monday=time(18, 30),
        saturday_is_closed=True,
        work_start_saturday=None,
        work_end_saturday=None,
    )

    data = settings.to_dict()

    assert data["step_minutes"] == "15"
    assert data["default_buffer_between_minutes"] == "5"
    assert data["min_advance_minutes"] == "30"
    assert data["max_advance_days"] == "14"
    assert data["work_start_monday"] == "09:00:00"
    assert data["work_end_monday"] == "18:30:00"
    assert data["monday_is_closed"] == "False"
    assert data["saturday_is_closed"] == "True"
    assert data["work_start_saturday"] is None
    assert "id" not in data
    assert "pk" not in data


def test_booking_settings_sync_skips_when_debug_redis_is_disabled():
    settings = ConcreteBookingSettingsSync()
    settings.to_dict = MagicMock(return_value={"step_minutes": "30"})  # type: ignore[method-assign]

    with (
        override_settings(DEBUG=True, CODEX_REDIS_ENABLED=False),
        patch("codex_django.core.redis.managers.booking.get_booking_cache_manager") as mock_get_manager,
    ):
        settings.sync_booking_settings_to_redis()

    mock_get_manager.assert_not_called()


def test_booking_settings_sync_writes_serialized_payload_to_manager():
    settings = ConcreteBookingSettingsSync()
    settings.to_dict = MagicMock(return_value={"step_minutes": "30"})  # type: ignore[method-assign]
    manager = MagicMock()
    manager.make_key.return_value = "booking:settings"
    sync_set = MagicMock()

    with (
        override_settings(DEBUG=False),
        patch("codex_django.core.redis.managers.booking.get_booking_cache_manager", return_value=manager),
        patch("asgiref.sync.async_to_sync", return_value=sync_set) as mock_async_to_sync,
    ):
        settings.sync_booking_settings_to_redis()

    manager.make_key.assert_called_once_with("settings")
    mock_async_to_sync.assert_called_once_with(manager.string.set)
    sync_set.assert_called_once_with("booking:settings", "{'step_minutes': '30'}")


def test_booking_settings_sync_skips_empty_payload():
    settings = ConcreteBookingSettingsSync()
    settings.to_dict = MagicMock(return_value={})  # type: ignore[method-assign]
    manager = MagicMock()

    with (
        override_settings(DEBUG=False),
        patch("codex_django.core.redis.managers.booking.get_booking_cache_manager", return_value=manager),
        patch("asgiref.sync.async_to_sync") as mock_async_to_sync,
    ):
        settings.sync_booking_settings_to_redis()

    manager.make_key.assert_not_called()
    mock_async_to_sync.assert_not_called()


def test_booking_settings_sync_skips_instances_without_to_dict():
    settings = ConcreteBookingSettingsSyncNoDict()
    manager = MagicMock()

    with (
        override_settings(DEBUG=False),
        patch("codex_django.core.redis.managers.booking.get_booking_cache_manager", return_value=manager),
    ):
        settings.sync_booking_settings_to_redis()

    manager.make_key.assert_not_called()


def test_booking_settings_sync_logs_warning_when_manager_fails():
    settings = ConcreteBookingSettingsSync()
    settings.to_dict = MagicMock(return_value={"step_minutes": "30"})  # type: ignore[method-assign]

    with (
        override_settings(DEBUG=False),
        patch("codex_django.core.redis.managers.booking.get_booking_cache_manager", side_effect=RuntimeError("boom")),
        patch("codex_django.booking.mixins.settings.log.warning") as mock_warning,
    ):
        settings.sync_booking_settings_to_redis()

    mock_warning.assert_called_once()


def test_abstract_booking_settings_composes_both_mixins():
    settings = ConcreteAbstractBookingSettings(step_minutes=45)

    assert isinstance(settings, BookingSettingsMixin)
    assert isinstance(settings, BookingSettingsSyncMixin)
    assert settings.to_dict()["step_minutes"] == "45"


def test_booking_settings_get_day_schedule_respects_closed_flag():
    settings = ConcreteBookingSettings(
        monday_is_closed=False,
        work_start_monday=time(8, 0),
        work_end_monday=time(17, 0),
        sunday_is_closed=True,
    )

    assert settings.get_day_schedule(0) == (time(8, 0), time(17, 0))
    assert settings.get_day_schedule(6) is None
