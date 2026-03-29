"""Base Redis manager utilities adapted to Django settings.

This module is the bridge between codex-platform Redis helpers and the Django
settings conventions used by codex-django projects.
"""

from typing import Any

from codex_platform.redis_service.managers.base_manager import BaseRedisManager
from django.conf import settings
from redis.asyncio import Redis


class BaseDjangoRedisManager(BaseRedisManager):  # type: ignore[misc]
    """Base Redis manager adapted for Django settings and project namespacing."""

    def __init__(self, prefix: str = "", **kwargs: Any) -> None:
        self.redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        client: Any = Redis.from_url(self.redis_url, decode_responses=True)
        super().__init__(client)

        self.project_name = getattr(settings, "PROJECT_NAME", "")
        self.prefix = prefix

    def make_key(self, key: str) -> str:
        """Build a namespaced Redis key for the current Django project.

        Args:
            key: Logical key suffix for the concrete cache entry.

        Returns:
            A colon-delimited Redis key in the
            ``{PROJECT_NAME}:{prefix}:{key}`` format with empty segments
            omitted.
        """
        parts = [p for p in (self.project_name, self.prefix, key) if p]
        return ":".join(parts)

    def _is_disabled(self) -> bool:
        """Return ``True`` when Redis-backed behavior is disabled locally."""
        return bool(settings.DEBUG and not getattr(settings, "CODEX_REDIS_ENABLED", False))
