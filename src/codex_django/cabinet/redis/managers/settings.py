"""Redis manager for cabinet settings payloads."""

from typing import Any

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
        async with self.async_hash() as hash_ops:
            return await hash_ops.get_all(self.make_key(self._KEY)) or {}

    def get(self) -> dict[str, Any]:
        """Synchronously return the cached cabinet settings payload."""
        if self._is_disabled():
            return {}
        with self.sync_hash() as hash_ops:
            return hash_ops.get_all(self.make_key(self._KEY)) or {}

    async def asave_instance(self, instance: Any) -> None:
        """Asynchronously persist a cabinet settings instance to Redis.

        Args:
            instance: Object implementing ``to_cabinet_dict()``.
        """
        if self._is_disabled():
            return
        data = instance.to_cabinet_dict()
        if data:
            async with self.async_hash() as hash_ops:
                await hash_ops.set_fields(self.make_key(self._KEY), data)

    def save_instance(self, instance: Any) -> None:
        """Synchronously persist a cabinet settings instance to Redis."""
        if self._is_disabled():
            return
        data = instance.to_cabinet_dict()
        if data:
            with self.sync_hash() as hash_ops:
                hash_ops.set_fields(self.make_key(self._KEY), data)

    async def ainvalidate(self) -> None:
        """Asynchronously invalidate the cached cabinet settings payload."""
        if self._is_disabled():
            return
        async with self.async_string() as string:
            await string.delete(self.make_key(self._KEY))

    def invalidate(self) -> None:
        """Synchronously invalidate the cached cabinet settings payload."""
        if self._is_disabled():
            return
        with self.sync_string() as string:
            string.delete(self.make_key(self._KEY))
