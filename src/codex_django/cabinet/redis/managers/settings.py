"""Redis manager for cabinet settings payloads."""

from typing import Any

from asgiref.sync import async_to_sync

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class CabinetSettingsRedisManager(BaseDjangoRedisManager):
    """Sync/async manager for CabinetSettings in Redis.

    Key format: {PROJECT_NAME}:cabinet:settings
    Uses Redis Hash (same pattern as DjangoSiteSettingsManager).
    Respects DEBUG mode + CODEX_REDIS_ENABLED flag — safe for local dev without Redis.
    """

    _KEY = "site_settings"

    def __init__(self) -> None:
        super().__init__(prefix="")

    async def aget(self) -> dict[str, Any]:
        """Asynchronously return the cached cabinet settings payload.

        Returns:
            Cached cabinet settings data, or an empty dictionary when caching
            is disabled or the Redis hash does not exist.
        """
        if self._is_disabled():
            return {}
        return await self.hash.get_all(self.make_key(self._KEY)) or {}

    def get(self) -> dict[str, Any]:
        """Synchronously return the cached cabinet settings payload."""
        return async_to_sync(self.aget)()

    async def asave_instance(self, instance: Any) -> None:
        """Asynchronously persist a cabinet settings instance to Redis.

        Args:
            instance: Object implementing ``to_cabinet_dict()``.
        """
        if self._is_disabled():
            return
        data = instance.to_cabinet_dict()
        if data:
            await self.hash.set_fields(self.make_key(self._KEY), data)

    def save_instance(self, instance: Any) -> None:
        """Synchronously persist a cabinet settings instance to Redis."""
        async_to_sync(self.asave_instance)(instance)

    async def ainvalidate(self) -> None:
        """Asynchronously invalidate the cached cabinet settings payload."""
        if self._is_disabled():
            return
        await self.string.delete(self.make_key(self._KEY))

    def invalidate(self) -> None:
        """Synchronously invalidate the cached cabinet settings payload."""
        async_to_sync(self.ainvalidate)()
