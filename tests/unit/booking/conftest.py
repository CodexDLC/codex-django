from unittest.mock import MagicMock

import pytest


@pytest.fixture
def adapter_models():
    """Seven mock model classes for DjangoAvailabilityAdapter construction."""
    models = {
        k: MagicMock()
        for k in [
            "master",
            "appointment",
            "service",
            "working_day",
            "day_off",
            "booking_settings",
        ]
    }
    # Default STATUS_* constants
    models["appointment"].STATUS_PENDING = "pending"
    models["appointment"].STATUS_CONFIRMED = "confirmed"
    models["master"].STATUS_ACTIVE = "active"
    return models


@pytest.fixture
def mock_booking_manager():
    """Pre-configured BookingCacheManager mock."""
    mgr = MagicMock()
    mgr.get_busy.return_value = None
    mgr.set_busy.return_value = None
    mgr.invalidate_master_date.return_value = None
    return mgr
