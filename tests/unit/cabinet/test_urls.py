import pytest

from codex_django.cabinet.urls import urlpatterns

pytestmark = pytest.mark.unit


def test_cabinet_urls_expose_dashboard_and_site_settings_routes():
    names = {pattern.name for pattern in urlpatterns}
    assert names == {"dashboard", "site_settings", "site_settings_tab"}
