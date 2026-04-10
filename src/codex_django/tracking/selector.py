"""Read-only analytics selectors for tracking data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from codex_django.cabinet.types import ListItem, ListWidgetData, MetricWidgetData, TableColumn, TableWidgetData

from .manager import get_tracking_manager
from .settings import get_tracking_settings


def _date_window(days: int) -> list[date]:
    today = timezone.localdate()
    return [today - timedelta(days=offset) for offset in range(days - 1, -1, -1)]


def _merge_counts(db_counts: dict[str, int], redis_counts: dict[str, str] | None) -> dict[str, int]:
    merged = dict(db_counts)
    if redis_counts:
        for path, views in redis_counts.items():
            merged[path] = int(views)
    return merged


@dataclass(frozen=True)
class TrackingAnalyticsContext:
    """Dashboard-ready tracking analytics payload."""

    tracking_total_views: MetricWidgetData
    tracking_unique_visitors: MetricWidgetData
    tracking_tracked_pages: MetricWidgetData
    tracking_views_chart: dict[str, Any]
    tracking_top_pages: ListWidgetData
    tracking_recent_page_views: TableWidgetData

    def as_dict(self) -> dict[str, Any]:
        """Return the context as template-friendly keys.

        Returns:
            A plain dictionary keyed the same way cabinet templates and widget
            providers expect to receive tracking analytics payloads.
        """

        return {
            "tracking_total_views": self.tracking_total_views,
            "tracking_unique_visitors": self.tracking_unique_visitors,
            "tracking_tracked_pages": self.tracking_tracked_pages,
            "tracking_views_chart": self.tracking_views_chart,
            "tracking_top_pages": self.tracking_top_pages,
            "tracking_recent_page_views": self.tracking_recent_page_views,
        }


class TrackingSelector:
    """Read page tracking analytics from Redis and flushed database rows."""

    @staticmethod
    def daily_counts(date_str: str | None = None) -> dict[str, int]:
        """Return path counters for a single day.

        Args:
            date_str: Optional ISO date string. Defaults to the current local
                day when omitted.

        Returns:
            A mapping of request path to total page views. Redis snapshots
            override ORM snapshot values when both are present.
        """
        from .models import PageView

        day = date_str or timezone.localdate().isoformat()
        db_counts = {
            row["path"]: int(row["views"])
            for row in PageView.objects.filter(date=day).values("path", "views").order_by("-views", "path")
        }
        return _merge_counts(db_counts, get_tracking_manager().get_daily(day))

    @staticmethod
    def top_pages(date_str: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        """Return the highest-traffic pages for one day.

        Args:
            date_str: Optional ISO date string. Defaults to the current local
                day when omitted.
            limit: Maximum number of rows to return.

        Returns:
            A list of ``{"path": ..., "views": ...}`` dictionaries ordered by
            descending view count and then by path.
        """

        counts = TrackingSelector.daily_counts(date_str)
        items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
        return [{"path": path, "views": views} for path, views in items]

    @staticmethod
    def unique_visitors(date_str: str | None = None) -> int:
        """Return the approximate unique visitor count for one day.

        Args:
            date_str: Optional ISO date string. Defaults to the current local
                day when omitted.

        Returns:
            The HyperLogLog-backed unique visitor estimate stored in Redis for
            the selected day.
        """

        day = date_str or timezone.localdate().isoformat()
        return get_tracking_manager().get_unique_count(day)

    @staticmethod
    def total_views(date_str: str | None = None) -> int:
        """Return total page views for one day.

        Args:
            date_str: Optional ISO date string. Defaults to the current local
                day when omitted.

        Returns:
            The sum of all page views for the selected day.
        """

        return sum(TrackingSelector.daily_counts(date_str).values())

    @staticmethod
    def multi_day_totals(days: int | None = None) -> list[dict[str, Any]]:
        """Return daily total views for a trailing analytics window.

        Args:
            days: Optional number of days to include. Falls back to
                ``TrackingSettings.analytics_days`` when omitted.

        Returns:
            A chronologically ordered list of ``{"date": ..., "views": ...}``
            dictionaries for each day in the requested window.
        """

        from .models import PageView

        resolved_days = days or get_tracking_settings().analytics_days
        dates = _date_window(resolved_days)
        totals = {day.isoformat(): 0 for day in dates}

        rows = (
            PageView.objects.filter(date__gte=dates[0], date__lte=dates[-1])
            .values("date")
            .annotate(total=Sum("views"))
            .order_by("date")
        )
        for row in rows:
            totals[row["date"].isoformat()] = int(row["total"] or 0)

        redis_snapshots = get_tracking_manager().get_multi_day([day.isoformat() for day in dates])
        for day, snapshot in zip(dates, redis_snapshots, strict=False):
            if snapshot:
                totals[day.isoformat()] = sum(int(value) for value in snapshot.values())

        return [{"date": day.isoformat(), "views": totals[day.isoformat()]} for day in dates]

    @staticmethod
    def get_analytics_context(days: int | None = None) -> TrackingAnalyticsContext:
        """Build cabinet-ready widget payloads for tracking analytics.

        Args:
            days: Optional number of trailing days to use for chart
                aggregation. Falls back to the configured analytics window.

        Returns:
            A typed ``TrackingAnalyticsContext`` containing KPI, chart, list,
            and table widgets for cabinet dashboards or analytics pages.
        """

        totals = TrackingSelector.multi_day_totals(days)
        today_total = totals[-1]["views"] if totals else 0
        yesterday_total = totals[-2]["views"] if len(totals) > 1 else 0
        tracked_pages = len(TrackingSelector.daily_counts())
        unique_visitors = TrackingSelector.unique_visitors()
        top_pages = TrackingSelector.top_pages(limit=8)

        trend_value = ""
        trend_direction = "neutral"
        if yesterday_total:
            diff = ((today_total - yesterday_total) / yesterday_total) * 100
            trend_value = f"{diff:+.0f}%"
            trend_direction = "up" if diff >= 0 else "down"

        chart_labels = [item["date"][5:] for item in totals]
        chart_values = [item["views"] for item in totals]

        return TrackingAnalyticsContext(
            tracking_total_views=MetricWidgetData(
                label=str(_("Page views today")),
                value=str(today_total),
                trend_value=trend_value or None,
                trend_label=str(_("vs yesterday")) if trend_value else None,
                trend_direction=trend_direction,
                icon="bi-eye",
            ),
            tracking_unique_visitors=MetricWidgetData(
                label=str(_("Unique visitors today")),
                value=str(unique_visitors),
                trend_label=str(_("live estimate")),
                icon="bi-person-check",
            ),
            tracking_tracked_pages=MetricWidgetData(
                label=str(_("Tracked pages today")),
                value=str(tracked_pages),
                icon="bi-file-earmark-bar-graph",
            ),
            tracking_views_chart={
                "chart_id": "trackingViewsChart",
                "title": str(_("Visits")),
                "subtitle": str(_("last 30 days")),
                "icon": "bi-graph-up",
                "type": "line",
                "kpi_value": str(sum(chart_values)),
                "kpi_trend_label": str(_("total views")),
                "chart_labels": chart_labels,
                "datasets": [
                    {
                        "label": str(_("Views")),
                        "data": chart_values,
                        "borderColor": "#2563eb",
                        "backgroundColor": "rgba(37,99,235,0.08)",
                        "fill": True,
                        "tension": 0,
                        "borderWidth": 2,
                        "pointRadius": 0,
                    }
                ],
            },
            tracking_top_pages=ListWidgetData(
                title=str(_("Top pages")),
                subtitle=str(_("today")),
                icon="bi-trophy",
                items=[
                    ListItem(label=row["path"], value=str(row["views"]), sublabel=str(_("views"))) for row in top_pages
                ],
            ),
            tracking_recent_page_views=TableWidgetData(
                columns=[
                    TableColumn(key="path", label=str(_("Path")), bold=True),
                    TableColumn(key="views", label=str(_("Views")), align="right"),
                ],
                rows=top_pages,
            ),
        )
