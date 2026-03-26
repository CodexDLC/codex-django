from typing import Any

from codex_platform.redis_service.managers.base_manager import BaseRedisManager
from django.conf import settings
from redis.asyncio import Redis


class BaseDjangoRedisManager(BaseRedisManager):  # type: ignore[misc]
    """Base manager for Django that inherits from platform's BaseRedisManager."""

    def __init__(self, prefix: str = "", **kwargs: Any) -> None:
        self.redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        client: Any = Redis.from_url(self.redis_url, decode_responses=True)
        super().__init__(client)

        self.project_name = getattr(settings, "PROJECT_NAME", "")
        self.prefix = prefix

    def make_key(self, key: str) -> str:
        """Формирует ключ в формате {PROJECT_NAME}:{prefix}:{key}"""
        parts = [p for p in (self.project_name, self.prefix, key) if p]
        return ":".join(parts)

    def _is_disabled(self) -> bool:
        """Проверяет, отключен ли Redis локально в DEBUG-режиме."""
        return bool(settings.DEBUG and not getattr(settings, "CODEX_REDIS_ENABLED", False))
