from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from codex_django.cabinet.views.dashboard import dashboard_view
from codex_django.cabinet.views.site_settings import site_settings_tab_view, site_settings_view

pytestmark = pytest.mark.unit


def _authenticated_request(path: str, **headers: str):
    request = RequestFactory().get(path, **headers)
    request.user = SimpleNamespace(is_authenticated=True)
    return request


def test_dashboard_view_renders_selector_context():
    request = _authenticated_request("/cabinet/")

    with (
        patch("codex_django.cabinet.views.dashboard.DashboardSelector.get_context", return_value={"kpi": 7}) as mock_ctx,
        patch("codex_django.cabinet.views.dashboard.render", return_value=HttpResponse("ok")) as mock_render,
    ):
        response = dashboard_view(request)

    assert response.status_code == 200
    mock_ctx.assert_called_once_with(request)
    mock_render.assert_called_once_with(request, "cabinet/dashboard/index.html", {"kpi": 7})


def test_site_settings_view_defaults_to_contact_tab():
    request = _authenticated_request("/cabinet/site/settings/")

    with patch("codex_django.cabinet.views.site_settings.render", return_value=HttpResponse("ok")) as mock_render:
        response = site_settings_view(request)

    assert response.status_code == 200
    mock_render.assert_called_once_with(
        request,
        "cabinet/site_settings/index.html",
        {"active_tab": "contact"},
    )


def test_site_settings_tab_view_uses_partial_for_htmx_request():
    request = _authenticated_request("/cabinet/site/settings/geo/", HTTP_HX_REQUEST="true")

    with patch("codex_django.cabinet.views.site_settings.render", return_value=HttpResponse("ok")) as mock_render:
        response = site_settings_tab_view(request, "geo")

    assert response.status_code == 200
    mock_render.assert_called_once_with(
        request,
        "cabinet/site_settings/partials/_geo.html",
        {"active_tab": "geo"},
    )


def test_site_settings_tab_view_falls_back_to_contact_for_unknown_tab():
    request = _authenticated_request("/cabinet/site/settings/oops/")

    with patch("codex_django.cabinet.views.site_settings.render", return_value=HttpResponse("ok")) as mock_render:
        response = site_settings_tab_view(request, "oops")

    assert response.status_code == 200
    mock_render.assert_called_once_with(
        request,
        "cabinet/site_settings/index.html",
        {"active_tab": "contact"},
    )
