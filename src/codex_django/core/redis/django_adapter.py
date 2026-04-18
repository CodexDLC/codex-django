"""Shared Redis builders for Django session and cache backends.

Provides the minimal surface needed by ``codex_django.sessions`` and
``codex_django.cache`` without going through ``BaseDjangoRedisManager``.

We intentionally do NOT reuse ``BaseDjangoRedisManager`` here because
session/cache backends must fail loud on Redis outage; the ``_is_disabled``
shortcut (used by domain managers in DEBUG mode) is wrong for them.
"""

from __future__ import annotations

from codex_platform.redis_service import RedisService
from django.conf import settings
from redis.asyncio import Redis


def _resolve_url(url: str | None) -> str:
    if url is not None:
        return url
    return str(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))


def build_redis_client(url: str | None = None) -> Redis:
    """Return an async Redis client with ``decode_responses=True``.

    Strings are always returned as ``str`` (not ``bytes``) to match the
    behavior relied upon by Django's session/cache layers.
    """
    client: Redis = Redis.from_url(_resolve_url(url), decode_responses=True)
    return client


def build_redis_service(url: str | None = None) -> RedisService:
    """Return a ``RedisService`` bound to an async Redis client."""
    return RedisService(build_redis_client(url))


def namespaced_key(prefix: str, key: str, *, project_name: str | None = None) -> str:
    """Build a colon-delimited Redis key: ``{PROJECT_NAME}:{prefix}:{key}``.

    Empty segments are omitted. Mirrors ``BaseDjangoRedisManager.make_key``.
    """
    if project_name is None:
        project_name = str(getattr(settings, "PROJECT_NAME", ""))
    parts = [p for p in (project_name, prefix, key) if p]
    return ":".join(parts)
