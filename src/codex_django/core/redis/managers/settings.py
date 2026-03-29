"""Redis-backed site settings storage helpers.

The settings manager caches the concrete project settings model in a single
Redis hash and exposes a lightweight proxy for template access.
"""

from typing import Any

from asgiref.sync import async_to_sync
from django.db import models

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class SettingsProxy:
    """Expose dictionary-backed settings through attribute-style access in templates.

    Args:
        data: Flat settings payload loaded from Redis or the database.
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def __getattr__(self, name: str) -> Any:
        """Return a setting value using attribute access semantics.

        Args:
            name: Setting key to resolve.

        Returns:
            The stored value, or an empty string when the key is missing.
        """
        return self.data.get(name, "")

    def __getitem__(self, name: str) -> Any:
        """Return a setting value using dictionary-style indexing.

        Args:
            name: Setting key to resolve.

        Returns:
            The stored value, or an empty string when the key is missing.
        """
        return self.data.get(name, "")


class DjangoSiteSettingsManager(BaseDjangoRedisManager):
    """Load and persist site settings in Redis with sync and async helpers.

    Notes:
        The manager stores one project-wide settings payload in a single
        Redis hash identified by ``site_settings``.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(prefix="", **kwargs)
        self.CACHE_KEY = "site_settings"

    async def aload_cached(self, model_cls: type[models.Model]) -> dict[str, Any]:
        """Load cached site settings from Redis asynchronously.

        Args:
            model_cls: Django model class for the concrete site settings
                model. The argument is accepted for API symmetry with
                :meth:`load_cached`.

        Returns:
            Cached settings data, or an empty dictionary when caching is
            disabled or no Redis entry exists.
        """
        if self._is_disabled():
            return {}
        result = await self.hash.get_all(self.make_key(self.CACHE_KEY))
        return result or {}

    def load_cached(self, model_cls: type[models.Model]) -> dict[str, Any]:
        """Load cached settings or fall back to the first database row.

        Args:
            model_cls: Django model class that stores the singleton site
                settings payload and optionally implements ``to_dict()``.

        Returns:
            Cached or freshly loaded site settings data.
        """
        data = async_to_sync(self.aload_cached)(model_cls)
        if not data:
            instance = model_cls.objects.first()  # type: ignore[attr-defined]
            if instance and hasattr(instance, "to_dict"):
                data = instance.to_dict()
                self.save_instance(instance)
        return data

    async def asave_instance(self, instance: models.Model) -> None:
        """Persist a settings instance to Redis asynchronously.

        Args:
            instance: Concrete site settings model instance that implements
                ``to_dict()``.
        """
        if self._is_disabled() or not hasattr(instance, "to_dict"):
            return
        data = instance.to_dict()
        if data:
            await self.hash.set_fields(self.make_key(self.CACHE_KEY), data)

    def save_instance(self, instance: models.Model) -> None:
        """Synchronously persist a settings instance to Redis.

        Args:
            instance: Concrete site settings model instance that implements
                ``to_dict()``.
        """
        async_to_sync(self.asave_instance)(instance)


def get_site_settings_manager() -> DjangoSiteSettingsManager:
    """Return a site settings manager configured from Django settings.

    Returns:
        A ready-to-use :class:`DjangoSiteSettingsManager` instance.
    """
    return DjangoSiteSettingsManager()
