"""
DjangoCacheAdapter
==================
ContentCacheAdapter implementation using BaseDjangoRedisManager.

A thin infrastructure shim — the caching strategy (key naming, TTL,
invalidation) lives in BaseEmailContentSelector, not here.

Usage::

    cache_adapter = DjangoCacheAdapter()
    value = cache_adapter.get("my:cache:key")
    cache_adapter.set("my:cache:key", "value", timeout=3600)
"""

from __future__ import annotations

from codex_django.core.redis.managers.notifications import get_notifications_cache_manager


class DjangoCacheAdapter:
    """
    Implements ContentCacheAdapter Protocol from codex_platform.notifications.interfaces.

    Delegates to codex_django NotificationsCacheManager.
    """

    def get(self, key: str) -> str | None:
        manager = get_notifications_cache_manager()
        return manager.get(key)

    def set(self, key: str, value: str, timeout: int) -> None:
        manager = get_notifications_cache_manager()
        manager.set(key, value, timeout=timeout)
