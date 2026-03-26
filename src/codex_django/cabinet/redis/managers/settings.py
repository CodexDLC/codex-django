from typing import Any

from asgiref.sync import async_to_sync

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class CabinetSettingsRedisManager(BaseDjangoRedisManager):
    """Sync/async manager for CabinetSettings in Redis.

    Key format: {PROJECT_NAME}:cabinet:settings
    Uses Redis Hash (same pattern as DjangoSiteSettingsManager).
    Respects DEBUG mode + CODEX_REDIS_ENABLED flag — safe for local dev without Redis.
    """

    _KEY = "settings"

    def __init__(self) -> None:
        super().__init__(prefix="cabinet")

    async def aget(self) -> dict[str, Any]:
        if self._is_disabled():
            return {}
        return await self.hash.get_all(self.make_key(self._KEY)) or {}

    def get(self) -> dict[str, Any]:
        return async_to_sync(self.aget)()

    async def asave_instance(self, instance: Any) -> None:
        if self._is_disabled():
            return
        data = instance.to_cabinet_dict()
        if data:
            await self.hash.set_fields(self.make_key(self._KEY), data)

    def save_instance(self, instance: Any) -> None:
        async_to_sync(self.asave_instance)(instance)

    async def ainvalidate(self) -> None:
        if self._is_disabled():
            return
        await self.string.delete(self.make_key(self._KEY))

    def invalidate(self) -> None:
        async_to_sync(self.ainvalidate)()
