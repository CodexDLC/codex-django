"""Smoke tests for showcase routes."""

from unittest.mock import patch

import pytest
from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from codex_django.showcase import views

pytestmark = pytest.mark.unit


def test_showcase_index_renders_in_debug_mode():
    request = RequestFactory().get("/showcase/")

    with (
        override_settings(DEBUG=True),
        patch("codex_django.showcase.views.render", return_value=HttpResponse("Codex Showcase")) as mock_render,
    ):
        response = views.index(request)

    assert response.status_code == 200
    assert b"Codex Showcase" in response.content
    mock_render.assert_called_once_with(request, "showcase/index.html")


def test_showcase_notifications_views_render_in_debug_mode():
    log_request = RequestFactory().get("/showcase/notifications/")
    templates_request = RequestFactory().get("/showcase/notifications/templates/")

    with (
        override_settings(DEBUG=True),
        patch("codex_django.showcase.views.render", return_value=HttpResponse("Notifications Template")) as mock_render,
    ):
        log_response = views.notifications_log_view(log_request)
        templates_response = views.notifications_templates_view(templates_request)

    assert log_response.status_code == 200
    assert templates_response.status_code == 200
    assert b"Notifications" in log_response.content
    assert b"Template" in templates_response.content
    assert mock_render.call_count == 2
    assert mock_render.call_args_list[0].args[1] == "showcase/cabinet/notifications/log.html"
    assert mock_render.call_args_list[1].args[1] == "showcase/cabinet/notifications/templates.html"


@pytest.mark.parametrize(
    ("path", "view", "template"),
    [
        ("/showcase/dashboard/", views.dashboard_view, "showcase/cabinet/dashboard/index.html"),
        ("/showcase/staff/?segment=active&q=anna", views.staff_view, "showcase/cabinet/staff/index.html"),
        ("/showcase/clients/?segment=vip&q=emma", views.clients_view, "showcase/cabinet/clients/index.html"),
        (
            "/showcase/conversations/?folder=archived&topic=2&q=follow-up",
            views.conversations_view,
            "showcase/cabinet/conversations/index.html",
        ),
        ("/showcase/booking/", views.booking_view, "showcase/cabinet/booking/index.html"),
        (
            "/showcase/booking/appointments/?status=confirmed",
            views.booking_appointments_view,
            "showcase/cabinet/booking/appointments.html",
        ),
        ("/showcase/booking/new/", views.booking_new_view, "showcase/cabinet/booking/new.html"),
        (
            "/showcase/analytics/reports/?tab=team&period=week&staff=emma",
            views.reports_view,
            "showcase/cabinet/analytics/reports.html",
        ),
        (
            "/showcase/catalog/3/",
            lambda request: views.catalog_view(request, category_pk=3),
            "showcase/cabinet/catalog/index.html",
        ),
    ],
)
def test_showcase_data_views_render_expected_templates(path, view, template):
    request = RequestFactory().get(path)

    with (
        override_settings(DEBUG=True),
        patch("codex_django.showcase.views.render", return_value=HttpResponse("ok")) as mock_render,
    ):
        response = view(request)

    assert response.status_code == 200
    assert mock_render.call_args.args[1] == template
    assert isinstance(mock_render.call_args.args[2], dict)


def test_showcase_conversation_detail_renders_detail_when_found():
    request = RequestFactory().get("/showcase/conversations/1/")

    with (
        override_settings(DEBUG=True),
        patch("codex_django.showcase.views.render", return_value=HttpResponse("detail")) as mock_render,
    ):
        response = views.conversation_detail_view(request, pk=1)

    assert response.status_code == 200
    assert mock_render.call_args.args[1] == "showcase/cabinet/conversations/_detail.html"
    assert "conv" in mock_render.call_args.args[2]


def test_showcase_conversation_detail_renders_empty_when_not_found():
    request = RequestFactory().get("/showcase/conversations/999/")

    with (
        override_settings(DEBUG=True),
        patch("codex_django.showcase.views.render", return_value=HttpResponse("empty")) as mock_render,
    ):
        response = views.conversation_detail_view(request, pk=999)

    assert response.status_code == 200
    mock_render.assert_called_once_with(request, "showcase/cabinet/conversations/_empty.html")


def test_showcase_site_settings_redirects_to_default_tab():
    request = RequestFactory().get("/showcase/site/settings/")

    with (
        override_settings(DEBUG=True),
        patch("codex_django.showcase.views.redirect", return_value=HttpResponse(status=302)) as mock_redirect,
    ):
        response = views.site_settings_view(request)

    assert response.status_code == 302
    mock_redirect.assert_called_once_with("codex_showcase:site_settings_tab", tab="contact")


def test_showcase_site_settings_tab_renders_partial_for_htmx():
    request = RequestFactory().get("/showcase/site/settings/geo/", HTTP_HX_REQUEST="true")

    with (
        override_settings(DEBUG=True),
        patch("codex_django.showcase.views.render", return_value=HttpResponse("partial")) as mock_render,
    ):
        response = views.site_settings_tab_view(request, tab="geo")

    assert response.status_code == 200
    mock_render.assert_called_once_with(
        request,
        "showcase/cabinet/site_settings/partials/_geo.html",
        {"active_tab": "geo"},
    )


def test_showcase_site_settings_tab_falls_back_to_contact():
    request = RequestFactory().get("/showcase/site/settings/oops/")

    with (
        override_settings(DEBUG=True),
        patch("codex_django.showcase.views.render", return_value=HttpResponse("full")) as mock_render,
    ):
        response = views.site_settings_tab_view(request, tab="oops")

    assert response.status_code == 200
    mock_render.assert_called_once_with(
        request,
        "showcase/cabinet/site_settings/index.html",
        {"active_tab": "contact"},
    )


def test_showcase_is_blocked_when_debug_is_disabled():
    request = RequestFactory().get("/showcase/")

    with override_settings(DEBUG=False):
        response = views.index(request)

    assert response.status_code == 403
