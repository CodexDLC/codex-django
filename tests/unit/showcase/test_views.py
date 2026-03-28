"""Smoke tests for showcase routes."""

from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from codex_django.showcase import views


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


def test_showcase_is_blocked_when_debug_is_disabled():
    request = RequestFactory().get("/showcase/")

    with override_settings(DEBUG=False):
        response = views.index(request)

    assert response.status_code == 403
