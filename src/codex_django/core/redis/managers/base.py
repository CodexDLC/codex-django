"""Base Redis manager utilities adapted to Django settings.

This module is the bridge between codex-platform Redis operations and the Django
settings conventions used by codex-django projects.
"""

from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import cast

from codex_platform.redis_service.operations.hash import HashOperations
from codex_platform.redis_service.operations.string import StringOperations
from codex_platform.redis_service.operations.sync_hash import SyncHashOperations
from codex_platform.redis_service.operations.sync_string import SyncStringOperations
from django.conf import settings
from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis


class BaseDjangoRedisManager:
    """Base Redis manager adapted for Django settings and project namespacing."""

    def __init__(
        self,
        prefix: str = "",
        *,
        async_client_factory: Callable[[], AsyncRedis] | None = None,
        sync_client_factory: Callable[[], SyncRedis] | None = None,
    ) -> None:
        self.prefix = prefix
        self.project_name = getattr(settings, "PROJECT_NAME", "")
        self._redis_url = str(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
        self._async_factory = async_client_factory or self._default_async_factory
        self._sync_factory = sync_client_factory or self._default_sync_factory

    def _default_async_factory(self) -> AsyncRedis:
        from redis.asyncio import Redis

        return cast(AsyncRedis, Redis.from_url(self._redis_url, decode_responses=True))

    def _default_sync_factory(self) -> SyncRedis:
        import redis

        return redis.Redis.from_url(self._redis_url, decode_responses=True)

    @asynccontextmanager
    async def async_string(self) -> AsyncIterator[StringOperations]:
        client = self._async_factory()
        try:
            yield StringOperations(client)
        finally:
            await client.aclose()

    @asynccontextmanager
    async def async_hash(self) -> AsyncIterator[HashOperations]:
        client = self._async_factory()
        try:
            yield HashOperations(client)
        finally:
            await client.aclose()

    @contextmanager
    def sync_string(self) -> Iterator[SyncStringOperations]:
        client = self._sync_factory()
        try:
            yield SyncStringOperations(client)
        finally:
            client.close()

    @contextmanager
    def sync_hash(self) -> Iterator[SyncHashOperations]:
        client = self._sync_factory()
        try:
            yield SyncHashOperations(client)
        finally:
            client.close()

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


def get_default_redis_manager(prefix: str = "") -> BaseDjangoRedisManager:
    """Return a base Redis manager configured from Django settings."""
    return BaseDjangoRedisManager(prefix=prefix)
