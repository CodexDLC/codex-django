"""
codex_django.booking.adapters.cache
====================================
Thin adapter over BookingCacheManager for busy slot caching.

Follows the same pattern as ``notifications.adapters.cache_adapter.DjangoCacheAdapter``.
"""

from __future__ import annotations

from codex_django.core.redis.managers.booking import get_booking_cache_manager


class BookingCacheAdapter:
    """Delegates to BookingCacheManager.

    Used by DjangoAvailabilityAdapter to cache/invalidate busy intervals.
    """

    def get_busy(self, master_id: str, date_str: str) -> list[list[str]] | None:
        manager = get_booking_cache_manager()
        return manager.get_busy(master_id, date_str)

    def set_busy(
        self,
        master_id: str,
        date_str: str,
        intervals: list[list[str]],
        timeout: int = 300,
    ) -> None:
        manager = get_booking_cache_manager()
        manager.set_busy(master_id, date_str, intervals, timeout=timeout)

    def invalidate_master_date(self, master_id: str, date_str: str) -> None:
        manager = get_booking_cache_manager()
        manager.invalidate_master_date(master_id, date_str)
