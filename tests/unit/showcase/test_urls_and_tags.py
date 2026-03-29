import pytest

from codex_django.showcase.templatetags.showcase_extras import get_item
from codex_django.showcase.urls import urlpatterns

pytestmark = pytest.mark.unit


def test_showcase_urls_include_notification_routes():
    names = {pattern.name for pattern in urlpatterns}
    assert "notifications_log" in names
    assert "notifications_templates" in names


def test_showcase_get_item_filter_returns_dash_for_missing_key():
    assert get_item({"name": "Alice"}, "missing") == "—"
    assert get_item("not-a-dict", "missing") == "—"
