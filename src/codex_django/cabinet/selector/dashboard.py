"""
Dashboard Selector
==================
Single entry point for dashboard data providers.
Providers are registered through ``@extend`` and cached in Redis through
``DashboardRedisManager`` using JSON rather than pickle.

Example project usage:

    # cabinet/selector/dashboard.py inside the generated project
    from codex_django.cabinet.selector.dashboard import DashboardSelector
    from ..mock import CabinetMockData

    @DashboardSelector.extend(cache_key="base_stats", cache_ttl=300)
    def base_stats(request):
        return {"dashboard_stats": CabinetMockData.get_dashboard_stats()}

Adding a provider from a feature module such as booking:

    # features/booking/cabinet.py
    @DashboardSelector.extend(cache_key="booking_kpi", cache_ttl=300)
    def booking_kpi(request):
        return {"booking_kpi": BookingSelector.get_dashboard_kpi(request)}

Invalidating cached data from a model save hook:

    # features/booking/models/booking.py
    from codex_django.cabinet.selector.dashboard import DashboardSelector
    DashboardSelector.invalidate("booking_kpi")
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, cast

from ..redis.managers.dashboard import DashboardRedisManager
from ..types import ListWidgetData, MetricWidgetData, TableWidgetData

_manager = DashboardRedisManager()


class DashboardAdapter(ABC):
    """Base class for dashboard data adapters.

    Adapters are responsible for fetching and formatting data for specific
    widget types before the selector merges them into the template context.
    """

    @abstractmethod
    def get_data(self, request: Any) -> dict[str, Any]:
        """Fetch and return widget data as a dictionary payload."""
        pass


class MetricAdapter(DashboardAdapter):
    """Generic adapter for metric widgets."""

    def __init__(self, provider_fn: Callable[..., MetricWidgetData]):
        self.provider_fn = provider_fn

    def get_data(self, request: Any) -> dict[str, Any]:
        """Wrap metric payloads under the ``metric`` key."""
        data = self.provider_fn(request)
        return {"metric": data}


class TableAdapter(DashboardAdapter):
    """Generic adapter for table widgets."""

    def __init__(self, provider_fn: Callable[..., TableWidgetData]):
        self.provider_fn = provider_fn

    def get_data(self, request: Any) -> dict[str, Any]:
        """Wrap table payloads under the ``table`` key."""
        data = self.provider_fn(request)
        return {"table": data}


class ListAdapter(DashboardAdapter):
    """Generic adapter for list widgets."""

    def __init__(self, provider_fn: Callable[..., ListWidgetData]):
        self.provider_fn = provider_fn

    def get_data(self, request: Any) -> dict[str, Any]:
        """Wrap list payloads under the ``list`` key."""
        data = self.provider_fn(request)
        return {"list": data}


class DashboardSelector:
    """
    Extensible dashboard data aggregator with Redis caching.

    Each provider is a flat function (request) -> dict or a DashboardAdapter.
    Registered via @DashboardSelector.extend(cache_key=..., cache_ttl=...).
    """

    _providers: list[dict[str, Any]] = []

    @classmethod
    def extend(
        cls,
        fn_or_adapter: Callable[..., Any] | DashboardAdapter | None = None,
        *,
        cache_key: str = "",
        cache_ttl: int = 120,
    ) -> Any:
        """
        Register a dashboard data provider.

        Args:
            cache_key:  Redis key suffix. Defaults to function/class name.
            cache_ttl:  Seconds to cache. 0 = no cache (real-time).
        """

        def decorator(obj: Callable[..., Any] | DashboardAdapter) -> Any:
            if isinstance(obj, DashboardAdapter):
                fn = obj.get_data
                name = obj.__class__.__name__.lower()
            else:
                fn = obj
                name = obj.__name__

            cls._providers.append(
                {
                    "fn": fn,
                    "cache_key": cache_key or name,
                    "cache_ttl": cache_ttl,
                }
            )
            return obj

        if fn_or_adapter is not None:
            return decorator(fn_or_adapter)
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
        """Resolve one provider, using Redis when caching is enabled."""
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
