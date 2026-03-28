"""Redis-backed static content storage helpers."""

from typing import Any

from asgiref.sync import async_to_sync
from django.db import models

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


class StaticContentManager(BaseDjangoRedisManager):
    """Load and persist template static content in Redis."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(prefix="", **kwargs)
        self.cache_key = "static_content"

    async def aload_cached(self, model_cls: type[models.Model]) -> dict[str, str]:
        """Load cached static content from Redis asynchronously."""
        if self._is_disabled():
            return {}
        result = await self.hash.get_all(self.make_key(self.cache_key))
        return result or {}

    def load_cached(self, model_cls: type[models.Model]) -> dict[str, str]:
        """Load cached static content or populate it from the database."""
        data = async_to_sync(self.aload_cached)(model_cls)
        if not data:
            rows = model_cls.objects.all()  # type: ignore[attr-defined]
            data = {str(obj.key): str(obj.content) for obj in rows}
            if data:
                self.save_mapping(data)
        return data

    async def asave_mapping(self, data: dict[str, str]) -> None:
        """Persist a static-content mapping to Redis asynchronously."""
        if self._is_disabled() or not data:
            return
        await self.hash.set_fields(self.make_key(self.cache_key), data)

    def save_mapping(self, data: dict[str, str]) -> None:
        """Synchronously persist a static-content mapping to Redis."""
        async_to_sync(self.asave_mapping)(data)


def get_static_content_manager() -> StaticContentManager:
    """Return a static-content manager configured from Django settings."""
    return StaticContentManager()
