"""
codex_django.core.redis.managers.booking
=========================================
Redis cache manager for booking busy slot intervals.

Caches **busy intervals** (not free slots) per master per date.
ChainFinder computes free slots on the fly — cheap math when busy data is in memory.

Invalidation is surgical: master_id + date.
"""

import json
from typing import Any

from asgiref.sync import async_to_sync

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class BookingCacheManager(BaseDjangoRedisManager):
    """Cache for busy slot intervals.

    Key format: ``booking:busy:{master_id}:{date}``
    Value: JSON list of ``[[start_iso, end_iso], ...]``
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(prefix="booking", **kwargs)

    # ------------------------------------------------------------------
    # Async API
    # ------------------------------------------------------------------

    async def aget_busy(self, master_id: str, date_str: str) -> list[list[str]] | None:
        """Return cached busy intervals for a master on a date.

        Returns ``None`` when cache is empty (miss).
        """
        if self._is_disabled():
            return None
        raw = await self.string.get(self.make_key(f"busy:{master_id}:{date_str}"))
        if raw is None:
            return None
        return json.loads(raw)  # type: ignore[no-any-return]

    async def aset_busy(
        self,
        master_id: str,
        date_str: str,
        intervals: list[list[str]],
        timeout: int = 300,
    ) -> None:
        """Store busy intervals in cache."""
        if self._is_disabled():
            return
        key = self.make_key(f"busy:{master_id}:{date_str}")
        await self.string.set(key, json.dumps(intervals), ttl=timeout)

    async def ainvalidate_master_date(self, master_id: str, date_str: str) -> None:
        """Drop cached busy intervals for a specific master + date."""
        if self._is_disabled():
            return
        await self.string.delete(self.make_key(f"busy:{master_id}:{date_str}"))

    # ------------------------------------------------------------------
    # Sync wrappers
    # ------------------------------------------------------------------

    def get_busy(self, master_id: str, date_str: str) -> list[list[str]] | None:
        return async_to_sync(self.aget_busy)(master_id, date_str)

    def set_busy(
        self,
        master_id: str,
        date_str: str,
        intervals: list[list[str]],
        timeout: int = 300,
    ) -> None:
        async_to_sync(self.aset_busy)(master_id, date_str, intervals, timeout)

    def invalidate_master_date(self, master_id: str, date_str: str) -> None:
        async_to_sync(self.ainvalidate_master_date)(master_id, date_str)


def get_booking_cache_manager() -> BookingCacheManager:
    return BookingCacheManager()
