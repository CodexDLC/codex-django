"""Cabinet declarations for the reusable tracking app."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from codex_django.cabinet import DashboardWidget, SidebarItem, TopbarEntry, declare

from .settings import get_tracking_settings

_analytics_url = get_tracking_settings().analytics_url

declare(
    module="tracking",
    space="staff",
    topbar=TopbarEntry(
        group="admin",
        label=_("Analytics"),
        icon="bi-bar-chart",
        url=_analytics_url,
        order=30,
    ),
    sidebar=[
        SidebarItem(
            label=_("Visits"),
            url=_analytics_url,
            icon="bi-graph-up-arrow",
            order=10,
        ),
    ],
    dashboard_widgets=[
        DashboardWidget(
            template="cabinet/widgets/kpi.html",
            context_key="tracking_total_views",
            col="col-md-4",
            nav_group="admin",
            order=70,
        ),
        DashboardWidget(
            template="cabinet/widgets/chart.html",
            context_key="tracking_views_chart",
            col="col-lg-8",
            nav_group="admin",
            order=71,
        ),
        DashboardWidget(
            template="cabinet/widgets/list.html",
            context_key="tracking_top_pages",
            col="col-lg-4",
            nav_group="admin",
            order=72,
        ),
    ],
)
