"""Redis-backed site settings storage helpers.

The settings manager caches the concrete project settings model in a single
Redis hash and exposes a lightweight proxy for template access.
"""

from __future__ import annotations

import json
from typing import Any

from django.db import models
from django.db.models.fields import NOT_PROVIDED

from codex_django.cache.values import CacheCoder
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

    def _field_default(self, field: models.Field[Any, Any]) -> Any:
        default = getattr(field, "default", NOT_PROVIDED)
        if default is NOT_PROVIDED:
            return None if getattr(field, "null", False) else ""
        return default() if callable(default) else default

    def _decode_field(self, field: models.Field[Any, Any], raw: str) -> Any:
        if isinstance(field, models.BooleanField):
            if raw == "1":
                return True
            if raw == "0":
                return False
            if raw == "" and getattr(field, "null", False):
                return None
            return self._field_default(field)

        if isinstance(field, models.CharField | models.TextField):
            return raw

        if raw == "" and getattr(field, "null", False):
            return None

        if isinstance(field, models.DateTimeField):
            return CacheCoder.load_datetime(raw)
        if isinstance(field, models.DateField):
            return CacheCoder.load_date(raw)
        if isinstance(field, models.TimeField):
            return CacheCoder.load_time(raw)
        if isinstance(field, models.DecimalField):
            return CacheCoder.load_decimal(raw)
        if isinstance(field, models.UUIDField):
            return CacheCoder.load_uuid(raw)
        if isinstance(field, models.IntegerField):
            return int(raw)
        if isinstance(field, models.FloatField):
            return float(raw)
        if isinstance(field, models.JSONField):
            return json.loads(raw)

        return raw

    def _decode_fields(self, raw: dict[str, str], model_cls: type[models.Model]) -> dict[str, Any]:
        fields_by_name = self._fields_by_name(model_cls)
        if not fields_by_name:
            return raw

        decoded: dict[str, Any] = {}
        for name, value in raw.items():
            field = fields_by_name.get(name)
            if field is None:
                decoded[name] = value
                continue
            try:
                decoded[name] = self._decode_field(field, value)
            except (TypeError, ValueError, json.JSONDecodeError):
                decoded[name] = self._field_default(field)
        return decoded

    def _fields_by_name(self, model_cls: type[models.Model]) -> dict[str, models.Field[Any, Any]]:
        meta = getattr(model_cls, "_meta", None)
        if meta is None:
            return {}
        return {
            field.name: field
            for field in meta.get_fields()
            if isinstance(field, models.Field) and not field.many_to_many and not field.one_to_many
        }

    def _encode_fields(self, data: dict[str, Any], model_cls: type[models.Model]) -> dict[str, Any]:
        fields_by_name = self._fields_by_name(model_cls)
        encoded: dict[str, Any] = {}
        for name, value in data.items():
            field = fields_by_name.get(name)
            if isinstance(field, models.JSONField):
                from django.core.serializers.json import DjangoJSONEncoder

                encoded[name] = json.dumps(value, cls=DjangoJSONEncoder)
            else:
                encoded[name] = CacheCoder.dump(value)
        return encoded

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
        async with self.async_hash() as h:
            result = await h.get_all(self.make_key(self.CACHE_KEY))
        return self._decode_fields(result, model_cls) if result else {}

    def load_cached(self, model_cls: type[models.Model]) -> dict[str, Any]:
        """Load cached settings or fall back to the first database row.

        Args:
            model_cls: Django model class that stores the singleton site
                settings payload and optionally implements ``to_dict()``.

        Returns:
            Cached or freshly loaded site settings data.
        """
        data: dict[str, Any] | None
        if self._is_disabled():
            data = {}
        else:
            with self.sync_hash() as h:
                raw = h.get_all(self.make_key(self.CACHE_KEY))
                data = self._decode_fields(raw, model_cls) if raw else None

        if not data:
            instance = model_cls.objects.first()  # type: ignore[attr-defined]
            if instance and hasattr(instance, "to_dict"):
                data = instance.to_dict()
                self.save_instance(instance)
        return data or {}

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
            coded = self._encode_fields(data, type(instance))
            async with self.async_hash() as h:
                await h.set_fields(self.make_key(self.CACHE_KEY), coded)

    def save_instance(self, instance: models.Model) -> None:
        """Synchronously persist a settings instance to Redis.

        Args:
            instance: Concrete site settings model instance that implements
                ``to_dict()``.
        """
        if self._is_disabled() or not hasattr(instance, "to_dict"):
            return
        data = instance.to_dict()
        if data:
            coded = self._encode_fields(data, type(instance))
            with self.sync_hash() as h:
                h.set_fields(self.make_key(self.CACHE_KEY), coded)


def get_site_settings_manager() -> DjangoSiteSettingsManager:
    """Return a site settings manager configured from Django settings.

    Returns:
        A ready-to-use :class:`DjangoSiteSettingsManager` instance.
    """
    return DjangoSiteSettingsManager()
