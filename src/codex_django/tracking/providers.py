"""DashboardSelector providers for reusable tracking widgets."""

from __future__ import annotations

from typing import Any

from codex_django.cabinet.selector.dashboard import DashboardSelector

from .selector import TrackingSelector


@DashboardSelector.extend(cache_key="tracking_analytics", cache_ttl=60)
def provide_tracking_analytics(request: Any) -> dict[str, Any]:
    """Expose tracking analytics widgets to the cabinet dashboard."""

    return TrackingSelector.get_analytics_context().as_dict()
