"""
Dashboard Redis Manager
=======================
Redis cache for dashboard data. Each provider is stored under its own key.

Serialization uses JSON instead of pickle, which keeps values readable from
``redis-cli``. Supported value types are ``str``, ``int``, ``float``, ``bool``,
``list``, ``dict``, and ``Decimal`` converted to ``str``.

Key format: {PROJECT_NAME}:cabinet:dashboard:{provider_key}
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, cast

from asgiref.sync import async_to_sync

from codex_django.core.redis.managers.base import BaseDjangoRedisManager

# ─── JSON serialization ────────────────────────────────────────────────────────


class _Encoder(json.JSONEncoder):
    """Handles types not supported by stdlib JSON."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def _dumps(data: dict[str, Any]) -> str:
    """Serialize dashboard payload data to JSON."""
    return json.dumps(data, cls=_Encoder, ensure_ascii=False)


def _loads(raw: str) -> dict[str, Any]:
    """Deserialize dashboard payload data from JSON."""
    return cast(dict[str, Any], json.loads(raw))


# ─── Manager ──────────────────────────────────────────────────────────────────


class DashboardRedisManager(BaseDjangoRedisManager):
    """
    Per-provider Redis cache for dashboard data.

    Usage in DashboardSelector:
        _manager = DashboardRedisManager()

        cached = _manager.get("booking_kpi")
        if cached is None:
            data = expensive_query()
            _manager.set("booking_kpi", data, ttl=300)

    Invalidation from model signal / lifecycle hook:
        _manager.invalidate("booking_kpi")   # one provider
        _manager.invalidate_all()            # full dashboard refresh
    """

    def __init__(self) -> None:
        super().__init__(prefix="cabinet:dashboard")

    # ── Read ──────────────────────────────────────────────────────────────────

    async def aget(self, provider_key: str) -> dict[str, Any] | None:
        """Return cached provider data or ``None`` on cache miss."""
        if self._is_disabled():
            return None
        raw = await self._client.get(self.make_key(provider_key))
        if raw is None:
            return None
        try:
            return _loads(raw)
        except (json.JSONDecodeError, ValueError):
            return None

    def get(self, provider_key: str) -> dict[str, Any] | None:
        """Synchronously return cached provider data."""
        return async_to_sync(self.aget)(provider_key)

    # ── Write ─────────────────────────────────────────────────────────────────

    async def aset(self, provider_key: str, data: dict[str, Any], ttl: int) -> None:
        """Store provider data with a TTL in seconds."""
        if self._is_disabled() or not data:
            return
        await self._client.set(
            self.make_key(provider_key),
            _dumps(data),
            ex=ttl,
        )

    def set(self, provider_key: str, data: dict[str, Any], ttl: int) -> None:
        """Synchronously store provider data with a TTL in seconds."""
        async_to_sync(self.aset)(provider_key, data, ttl)

    # ── Invalidation ──────────────────────────────────────────────────────────

    async def ainvalidate(self, provider_key: str) -> None:
        """Delete cache for a single provider."""
        if self._is_disabled():
            return
        await self._client.delete(self.make_key(provider_key))

    def invalidate(self, provider_key: str) -> None:
        """Synchronously delete cache for a single provider."""
        async_to_sync(self.ainvalidate)(provider_key)

    async def ainvalidate_all(self) -> None:
        """Delete all dashboard provider caches using a key pattern."""
        if self._is_disabled():
            return
        pattern = self.make_key("*")
        keys = await self._client.keys(pattern)
        if keys:
            await self._client.delete(*keys)

    def invalidate_all(self) -> None:
        """Synchronously delete all dashboard provider caches."""
        async_to_sync(self.ainvalidate_all)()
