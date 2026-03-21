"""
DjangoCacheAdapter
==================
ContentCacheAdapter implementation using Django's cache framework.

A thin infrastructure shim — the caching strategy (key naming, TTL,
invalidation) lives in BaseEmailContentSelector, not here.

Usage::

    cache_adapter = DjangoCacheAdapter()
    value = cache_adapter.get("my:cache:key")
    cache_adapter.set("my:cache:key", "value", timeout=3600)
"""

from __future__ import annotations


class DjangoCacheAdapter:
    """
    Implements ContentCacheAdapter Protocol from codex_platform.notifications.interfaces.

    Delegates to Django's configured cache backend (CACHES in settings).
    """

    def get(self, key: str) -> str | None:
        from django.core.cache import cache

        return cache.get(key)  # type: ignore[no-any-return]

    def set(self, key: str, value: str, timeout: int) -> None:
        from django.core.cache import cache

        cache.set(key, value, timeout)
