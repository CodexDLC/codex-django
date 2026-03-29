"""Django-facing ARQ adapter built on top of codex-platform delivery primitives."""

from __future__ import annotations

from typing import Any, Protocol, cast
from urllib.parse import urlparse

from asgiref.sync import async_to_sync
from django.conf import settings


class _ArqAdapterProtocol(Protocol):
    """Minimal protocol expected from the platform ARQ notification adapter."""

    def enqueue(self, task_name: str, payload: dict[str, Any]) -> str | None: ...

    async def enqueue_async(self, task_name: str, payload: dict[str, Any]) -> str | None: ...


class DjangoArqClient:
    """Thin Django-friendly wrapper around codex-platform's ARQ adapter."""

    def __init__(
        self,
        *,
        adapter: _ArqAdapterProtocol | None = None,
        pool: Any | None = None,
        redis_settings: Any | None = None,
    ) -> None:
        self._pool: Any | None = pool
        self._adapter: _ArqAdapterProtocol | None = adapter
        self._redis_settings: Any | None = redis_settings

    @staticmethod
    def build_redis_settings_from_django() -> Any:
        """Build ARQ RedisSettings from Django settings as a convenience fallback."""
        from arq.connections import RedisSettings

        redis_url = getattr(settings, "ARQ_REDIS_URL", None) or getattr(settings, "REDIS_URL", None)
        if redis_url:
            parsed = urlparse(str(redis_url))
            database = int(parsed.path.lstrip("/") or "0")
            return RedisSettings(
                host=parsed.hostname or "localhost",
                port=parsed.port or 6379,
                username=parsed.username,
                password=parsed.password,
                database=database,
                ssl=parsed.scheme == "rediss",
            )

        return RedisSettings(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=int(getattr(settings, "REDIS_PORT", 6379)),
            password=getattr(settings, "REDIS_PASSWORD", None),
            database=int(getattr(settings, "REDIS_DB", 0)),
        )

    async def _get_adapter(self) -> _ArqAdapterProtocol:
        """Lazily create the underlying codex-platform ARQ adapter."""
        if self._adapter is None:
            from arq.connections import create_pool
            from codex_platform.notifications.delivery import ArqNotificationAdapter

            if self._pool is None:
                redis_settings = self._redis_settings or self.build_redis_settings_from_django()
                self._pool = await create_pool(redis_settings)
            self._adapter = cast(_ArqAdapterProtocol, ArqNotificationAdapter(self._pool))
        return self._adapter

    def enqueue(self, task_name: str, payload: dict[str, Any]) -> str | None:
        """Enqueue a task synchronously via the platform ARQ adapter."""
        adapter = async_to_sync(self._get_adapter)()
        return adapter.enqueue(task_name, payload)

    async def aenqueue(self, task_name: str, payload: dict[str, Any]) -> str | None:
        """Enqueue a task asynchronously via the platform ARQ adapter."""
        adapter = await self._get_adapter()
        return await adapter.enqueue_async(task_name, payload)
