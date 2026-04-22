"""Redis manager for lightweight notification-related cache entries."""

from typing import Any

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class NotificationsCacheManager(BaseDjangoRedisManager):
    """Read and write notification-related cache entries in Redis.

    Notes:
        This manager is intentionally generic and stores simple key/value
        entries for notification subjects, templates, or other derived
        metadata that benefits from Redis-backed reuse.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(prefix="notif", **kwargs)

    async def aget(self, key: str) -> str | None:
        """Return a cached notification value by key, if present.

        Args:
            key: Logical cache key inside the notification namespace.

        Returns:
            The cached string value or ``None`` when the entry is missing.
        """
        if self._is_disabled():
            return None
        async with self.async_string() as s:
            return await s.get(self.make_key(key))  # type: ignore[no-any-return]

    async def aset(self, key: str, value: Any, timeout: int | None = None) -> None:
        """Store a notification cache value with an optional TTL.

        Args:
            key: Logical cache key inside the notification namespace.
            value: Value to store in Redis.
            timeout: Optional TTL in seconds.
        """
        if self._is_disabled():
            return
        async with self.async_string() as s:
            await s.set(self.make_key(key), value, ttl=timeout)

    def get(self, key: str) -> str | None:
        """Synchronously return a cached notification value.

        Args:
            key: Logical cache key inside the notification namespace.

        Returns:
            The cached string value or ``None`` when the entry is missing.
        """
        if self._is_disabled():
            return None
        with self.sync_string() as s:
            return s.get(self.make_key(key))  # type: ignore[no-any-return]

    def set(self, key: str, value: Any, timeout: int | None = None) -> None:
        """Synchronously store a notification cache value.

        Args:
            key: Logical cache key inside the notification namespace.
            value: Value to store in Redis.
            timeout: Optional TTL in seconds.
        """
        if self._is_disabled():
            return
        with self.sync_string() as s:
            s.set(self.make_key(key), value, ttl=timeout)


def get_notifications_cache_manager() -> NotificationsCacheManager:
    """Return a notifications cache manager configured from Django settings.

    Returns:
        A ready-to-use :class:`NotificationsCacheManager` instance.
    """
    return NotificationsCacheManager()
