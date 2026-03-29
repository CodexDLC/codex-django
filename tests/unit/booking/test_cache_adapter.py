"""Unit tests for BookingCacheAdapter."""

from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit


def _make_adapter(mock_manager):
    from codex_django.booking.adapters.cache import BookingCacheAdapter

    with patch(
        "codex_django.booking.adapters.cache.get_booking_cache_manager",
        return_value=mock_manager,
    ):
        return BookingCacheAdapter()


class TestBookingCacheAdapterGetBusy:
    def test_returns_cached_intervals(self, mock_booking_manager):
        from codex_django.booking.adapters.cache import BookingCacheAdapter

        mock_booking_manager.get_busy.return_value = [["09:00", "10:00"]]
        with patch(
            "codex_django.booking.adapters.cache.get_booking_cache_manager",
            return_value=mock_booking_manager,
        ):
            result = BookingCacheAdapter().get_busy("42", "2025-01-15")
        mock_booking_manager.get_busy.assert_called_once_with("42", "2025-01-15")
        assert result == [["09:00", "10:00"]]

    def test_returns_none_on_cache_miss(self, mock_booking_manager):
        from codex_django.booking.adapters.cache import BookingCacheAdapter

        mock_booking_manager.get_busy.return_value = None
        with patch(
            "codex_django.booking.adapters.cache.get_booking_cache_manager",
            return_value=mock_booking_manager,
        ):
            assert BookingCacheAdapter().get_busy("42", "2025-01-15") is None

    def test_passes_correct_args(self, mock_booking_manager):
        from codex_django.booking.adapters.cache import BookingCacheAdapter

        mock_booking_manager.get_busy.return_value = None
        with patch(
            "codex_django.booking.adapters.cache.get_booking_cache_manager",
            return_value=mock_booking_manager,
        ):
            BookingCacheAdapter().get_busy("99", "2026-06-01")
        mock_booking_manager.get_busy.assert_called_once_with("99", "2026-06-01")


class TestBookingCacheAdapterSetBusy:
    def test_delegates_with_default_timeout(self, mock_booking_manager):
        from codex_django.booking.adapters.cache import BookingCacheAdapter

        with patch(
            "codex_django.booking.adapters.cache.get_booking_cache_manager",
            return_value=mock_booking_manager,
        ):
            BookingCacheAdapter().set_busy("42", "2025-01-15", [["09:00", "10:00"]])
        mock_booking_manager.set_busy.assert_called_once_with("42", "2025-01-15", [["09:00", "10:00"]], timeout=300)

    def test_delegates_with_custom_timeout(self, mock_booking_manager):
        from codex_django.booking.adapters.cache import BookingCacheAdapter

        with patch(
            "codex_django.booking.adapters.cache.get_booking_cache_manager",
            return_value=mock_booking_manager,
        ):
            BookingCacheAdapter().set_busy("42", "2025-01-15", [], timeout=60)
        mock_booking_manager.set_busy.assert_called_once_with("42", "2025-01-15", [], timeout=60)

    def test_empty_intervals_accepted(self, mock_booking_manager):
        from codex_django.booking.adapters.cache import BookingCacheAdapter

        with patch(
            "codex_django.booking.adapters.cache.get_booking_cache_manager",
            return_value=mock_booking_manager,
        ):
            BookingCacheAdapter().set_busy("1", "2025-06-01", [], timeout=10)
        mock_booking_manager.set_busy.assert_called_once()


class TestBookingCacheAdapterInvalidate:
    def test_delegates_invalidate(self, mock_booking_manager):
        from codex_django.booking.adapters.cache import BookingCacheAdapter

        with patch(
            "codex_django.booking.adapters.cache.get_booking_cache_manager",
            return_value=mock_booking_manager,
        ):
            BookingCacheAdapter().invalidate_master_date("42", "2025-01-15")
        mock_booking_manager.invalidate_master_date.assert_called_once_with("42", "2025-01-15")

    def test_factory_called_per_method_call(self, mock_booking_manager):
        """Adapter calls get_booking_cache_manager() inside each method — no caching."""
        from codex_django.booking.adapters.cache import BookingCacheAdapter

        adapter = BookingCacheAdapter()
        with patch(
            "codex_django.booking.adapters.cache.get_booking_cache_manager",
            return_value=mock_booking_manager,
        ) as factory:
            adapter.invalidate_master_date("1", "2025-01-01")
            adapter.invalidate_master_date("2", "2025-01-02")
        assert factory.call_count == 2
