from typing import Any

from asgiref.sync import async_to_sync

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class NotificationsCacheManager(BaseDjangoRedisManager):
    """Manager to handle notifications caching in Redis."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(prefix="notif", **kwargs)

    async def aget(self, key: str) -> str | None:
        if self._is_disabled():
            return None
        return await self.string.get(self.make_key(key))  # type: ignore[no-any-return]

    async def aset(self, key: str, value: Any, timeout: int | None = None) -> None:
        if self._is_disabled():
            return
        await self.string.set(self.make_key(key), value, ttl=timeout)

    def get(self, key: str) -> str | None:
        return async_to_sync(self.aget)(key)

    def set(self, key: str, value: Any, timeout: int | None = None) -> None:
        async_to_sync(self.aset)(key, value, timeout)


def get_notifications_cache_manager() -> NotificationsCacheManager:
    return NotificationsCacheManager()
