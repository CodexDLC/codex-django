"""
Dashboard Selector
==================
Единая точка входа для данных дашборда. Провайдеры регистрируются через @extend.
Данные кэшируются в Redis через DashboardRedisManager (JSON, не pickle).

Паттерн использования в проекте:

    # cabinet/selector/dashboard.py (scaffold в проект)
    from codex_django.cabinet.selector.dashboard import DashboardSelector
    from ..mock import CabinetMockData

    @DashboardSelector.extend(cache_key="base_stats", cache_ttl=300)
    def base_stats(request):
        return {"dashboard_stats": CabinetMockData.get_dashboard_stats()}

Добавление провайдера из модуля (например, Booking):

    # features/booking/cabinet.py
    @DashboardSelector.extend(cache_key="booking_kpi", cache_ttl=300)
    def booking_kpi(request):
        return {"booking_kpi": BookingSelector.get_dashboard_kpi(request)}

Инвалидация при сохранении модели:

    # features/booking/models/booking.py
    from codex_django.cabinet.selector.dashboard import DashboardSelector
    DashboardSelector.invalidate("booking_kpi")
"""
from __future__ import annotations

from typing import Any, Callable, cast

from ..redis.managers.dashboard import DashboardRedisManager

_manager = DashboardRedisManager()


class DashboardSelector:
    """
    Extensible dashboard data aggregator with Redis caching.

    Each provider is a function (request) -> dict[str, Any].
    Registered via @DashboardSelector.extend(cache_key=..., cache_ttl=...).
    """

    _providers: list[dict[str, Any]] = []

    @classmethod
    def extend(
        cls,
        fn: Callable[..., Any] | None = None,
        *,
        cache_key: str = "",
        cache_ttl: int = 120,
    ) -> Any:
        """
        Register a dashboard data provider.

        Args:
            cache_key:  Redis key suffix. Defaults to function name.
            cache_ttl:  Seconds to cache. 0 = no cache (real-time).

        As decorator without args:
            @DashboardSelector.extend
            def my_stats(request): ...

        As decorator with args:
            @DashboardSelector.extend(cache_key="my_stats", cache_ttl=300)
            def my_stats(request): ...
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            cls._providers.append({
                "fn": func,
                "cache_key": cache_key or func.__name__,
                "cache_ttl": cache_ttl,
            })
            return func

        if fn is not None:
            # Used as @DashboardSelector.extend (no parentheses)
            return decorator(fn)
        return decorator

    @classmethod
    def get_context(cls, request: Any) -> dict[str, Any]:
        """
        Collect data from all registered providers.
        Each provider is read from Redis cache if available, otherwise called and cached.
        """
        context: dict[str, Any] = {}
        for provider in cls._providers:
            data = cls._resolve(provider, request)
            context.update(data)
        return context

    @classmethod
    def _resolve(cls, provider: dict[str, Any], request: Any) -> dict[str, Any]:
        cache_ttl = provider["cache_ttl"]
        cache_key = provider["cache_key"]

        if cache_ttl == 0:
            # Real-time: skip cache entirely
            return cast(dict[str, Any], provider["fn"](request))

        cached = _manager.get(cache_key)
        if cached is not None:
            return cached

        data = cast(dict[str, Any], provider["fn"](request))
        _manager.set(cache_key, data, ttl=cache_ttl)
        return data

    @classmethod
    def invalidate(cls, cache_key: str) -> None:
        """Invalidate cache for a specific provider. Call from model signals."""
        _manager.invalidate(cache_key)

    @classmethod
    def invalidate_all(cls) -> None:
        """Invalidate all dashboard provider caches."""
        _manager.invalidate_all()
