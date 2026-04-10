from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from codex_django.tracking.middleware import PageTrackingMiddleware

pytestmark = pytest.mark.unit


def _request(path: str = "/", *, authenticated: bool = True):
    request = RequestFactory().get(path)
    request.user = SimpleNamespace(is_authenticated=authenticated, pk=7)
    return request


@override_settings(CODEX_TRACKING={"track_anonymous": False})
def test_middleware_records_authenticated_get_response():
    request = _request("/about/")
    middleware = PageTrackingMiddleware(lambda req: HttpResponse("ok"))

    with patch("codex_django.tracking.recorder.TrackingRecorder.record") as record:
        response = middleware(request)

    assert response.status_code == 200
    record.assert_called_once_with(request)


@override_settings(CODEX_TRACKING={"track_anonymous": False})
def test_middleware_skips_anonymous_requests_by_default():
    request = _request("/about/", authenticated=False)
    middleware = PageTrackingMiddleware(lambda req: HttpResponse("ok"))

    with patch("codex_django.tracking.recorder.TrackingRecorder.record") as record:
        middleware(request)

    record.assert_not_called()


@override_settings(CODEX_TRACKING={"skip_prefixes": ["/assets/"], "track_anonymous": True})
def test_middleware_skips_configured_prefixes():
    request = _request("/assets/app.css", authenticated=False)
    middleware = PageTrackingMiddleware(lambda req: HttpResponse("ok"))

    with patch("codex_django.tracking.recorder.TrackingRecorder.record") as record:
        middleware(request)

    record.assert_not_called()
