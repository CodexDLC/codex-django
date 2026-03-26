from typing import Any

from asgiref.sync import async_to_sync
from django.db import models

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class SettingsProxy:
    """Provides a safe dictionary lookup for templates."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def __getattr__(self, name: str) -> Any:
        return self.data.get(name, "")

    def __getitem__(self, name: str) -> Any:
        return self.data.get(name, "")


class DjangoSiteSettingsManager(BaseDjangoRedisManager):
    """Sync/async manager to handle site settings in Redis."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(prefix="", **kwargs)
        self.CACHE_KEY = "site_settings"

    async def aload_cached(self, model_cls: type[models.Model]) -> dict[str, Any]:
        """Loads cached settings asynchronously."""
        if self._is_disabled():
            return {}
        result = await self.hash.get_all(self.make_key(self.CACHE_KEY))
        return result or {}

    def load_cached(self, model_cls: type[models.Model]) -> dict[str, Any]:
        """Loads cached settings or falls back to DB if missing."""
        data = async_to_sync(self.aload_cached)(model_cls)
        if not data:
            instance = model_cls.objects.first()  # type: ignore[attr-defined]
            if instance and hasattr(instance, "to_dict"):
                data = instance.to_dict()
                self.save_instance(instance)
        return data

    async def asave_instance(self, instance: models.Model) -> None:
        """Saves instance asynchronously."""
        if self._is_disabled() or not hasattr(instance, "to_dict"):
            return
        data = instance.to_dict()
        if data:
            await self.hash.set_fields(self.make_key(self.CACHE_KEY), data)

    def save_instance(self, instance: models.Model) -> None:
        async_to_sync(self.asave_instance)(instance)


def get_site_settings_manager() -> DjangoSiteSettingsManager:
    return DjangoSiteSettingsManager()
