from __future__ import annotations

import importlib
import io
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.contrib import admin
from django.core.management import call_command
from django.test import RequestFactory

from codex_django.tracking.admin import PageViewAdmin
from codex_django.tracking.models import PageView
from codex_django.tracking.recorder import TrackingRecorder

pytestmark = [pytest.mark.unit]


@pytest.mark.django_db
def test_flush_page_views_returns_zero_when_redis_snapshot_is_empty():
    with patch("codex_django.tracking.manager.get_tracking_manager") as get_manager:
        get_manager.return_value.get_daily.return_value = None

        from codex_django.tracking.flush import flush_page_views

        count = flush_page_views("2026-04-10")

    assert count == 0
    assert PageView.objects.count() == 0


@pytest.mark.django_db
def test_flush_page_views_upserts_daily_rows():
    PageView.objects.create(path="/about/", date=date(2026, 4, 10), views=2)

    with patch("codex_django.tracking.manager.get_tracking_manager") as get_manager:
        get_manager.return_value.get_daily.return_value = {
            "/about/": "5",
            "/pricing/": "3",
        }

        from codex_django.tracking.flush import flush_page_views

        count = flush_page_views("2026-04-10")

    assert count == 2
    assert list(PageView.objects.order_by("path").values_list("path", "views")) == [
        ("/about/", 5),
        ("/pricing/", 3),
    ]


def test_tracking_command_forwards_date_and_reports_flushed_count():
    out = io.StringIO()

    with patch("codex_django.tracking.flush.flush_page_views", return_value=4) as flush:
        call_command("flush_page_views", "--date", "2026-04-10", stdout=out)

    flush.assert_called_once_with("2026-04-10")
    assert "[codex-tracking] flushed 4 paths" in out.getvalue()


def test_tracking_recorder_uses_authenticated_user_pk():
    request = RequestFactory().get("/reports/")
    request.user = SimpleNamespace(is_authenticated=True, pk=42)

    with (
        patch("codex_django.tracking.recorder.timezone.localdate", return_value=date(2026, 4, 10)),
        patch("codex_django.tracking.manager.get_tracking_manager") as get_manager,
    ):
        TrackingRecorder.record(request)

    get_manager.return_value.record.assert_called_once_with("/reports/", "2026-04-10", "42")


def test_tracking_recorder_falls_back_to_root_and_omits_anonymous_user():
    request = SimpleNamespace(path="", user=SimpleNamespace(is_authenticated=False, pk=42))

    with (
        patch("codex_django.tracking.recorder.timezone.localdate", return_value=date(2026, 4, 10)),
        patch("codex_django.tracking.manager.get_tracking_manager") as get_manager,
    ):
        TrackingRecorder.record(request)

    get_manager.return_value.record.assert_called_once_with("/", "2026-04-10", None)


def test_tracking_urls_register_named_analytics_route():
    from codex_django.tracking.urls import app_name, urlpatterns

    assert app_name == "codex_tracking"
    assert len(urlpatterns) == 1
    assert urlpatterns[0].name == "analytics"
    assert urlpatterns[0].callback.__name__ == "tracking_analytics_view"


def test_tracking_provider_returns_dashboard_payload_dict():
    import codex_django.tracking.providers as providers

    payload = {"tracking_total_views": object()}

    with patch.object(providers.TrackingSelector, "get_analytics_context") as get_context:
        get_context.return_value.as_dict.return_value = payload

        result = providers.provide_tracking_analytics(SimpleNamespace())

    assert result is payload


def test_tracking_admin_registers_page_view_model():
    model_admin = admin.site._registry[PageView]

    assert isinstance(model_admin, PageViewAdmin)
    assert model_admin.list_display == ("date", "path", "views")
    assert model_admin.ordering == ("-date", "-views", "path")


def test_tracking_provider_decorator_registers_cache_metadata():
    import codex_django.tracking.providers as providers
    from codex_django.cabinet.selector.dashboard import DashboardSelector

    before = len(DashboardSelector._providers)

    importlib.reload(providers)

    assert len(DashboardSelector._providers) == before + 1
    assert DashboardSelector._providers[-1]["cache_key"] == "tracking_analytics"
    assert DashboardSelector._providers[-1]["cache_ttl"] == 60


def test_tracking_provider_module_import_is_stable():
    module = importlib.import_module("codex_django.tracking.providers")

    assert hasattr(module, "provide_tracking_analytics")
