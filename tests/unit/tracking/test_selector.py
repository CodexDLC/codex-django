from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from codex_django.tracking.models import PageView
from codex_django.tracking.selector import TrackingSelector

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


def test_top_pages_prefers_live_redis_counts_for_same_day():
    today = timezone.localdate()
    PageView.objects.create(path="/old/", date=today, views=3)
    PageView.objects.create(path="/live/", date=today, views=1)

    with patch("codex_django.tracking.selector.get_tracking_manager") as get_manager:
        get_manager.return_value.get_daily.return_value = {"/live/": "8", "/new/": "4"}
        rows = TrackingSelector.top_pages(limit=3)

    assert rows == [
        {"path": "/live/", "views": 8},
        {"path": "/new/", "views": 4},
        {"path": "/old/", "views": 3},
    ]


def test_multi_day_totals_uses_database_and_overlays_live_snapshots():
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    PageView.objects.create(path="/a/", date=yesterday, views=5)
    PageView.objects.create(path="/b/", date=today, views=2)

    with patch("codex_django.tracking.selector.get_tracking_manager") as get_manager:
        get_manager.return_value.get_multi_day.return_value = [None, {"/b/": "9", "/c/": "1"}]
        rows = TrackingSelector.multi_day_totals(days=2)

    assert rows == [
        {"date": yesterday.isoformat(), "views": 5},
        {"date": today.isoformat(), "views": 10},
    ]


def test_analytics_context_contains_dashboard_payloads():
    with patch("codex_django.tracking.selector.TrackingSelector.multi_day_totals") as totals:
        totals.return_value = [{"date": "2026-04-09", "views": 5}, {"date": "2026-04-10", "views": 10}]
        with (
            patch("codex_django.tracking.selector.TrackingSelector.top_pages") as top_pages,
            patch("codex_django.tracking.selector.TrackingSelector.unique_visitors", return_value=3),
        ):
            top_pages.side_effect = [
                [{"path": "/a/", "views": 10}],
                [{"path": "/a/", "views": 10}],
            ]
            context = TrackingSelector.get_analytics_context(days=2).as_dict()

    assert context["tracking_total_views"].value == "10"
    assert context["tracking_unique_visitors"].value == "3"
    assert context["tracking_views_chart"]["datasets"][0]["data"] == [5, 10]
    assert context["tracking_top_pages"].items[0].label == "/a/"
