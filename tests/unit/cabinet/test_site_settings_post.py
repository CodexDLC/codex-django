from unittest.mock import MagicMock, patch

import pytest
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpResponse
from django.test import RequestFactory

from codex_django.cabinet.views.site_settings import site_settings_view


@pytest.mark.unit
def test_site_settings_view_post_success():
    factory = RequestFactory()
    request = factory.post("/cabinet/site/settings/", data={"btn-save": "1"})

    # Add messages middleware support
    request.session = MagicMock()
    messages = FallbackStorage(request)
    request._messages = messages
    request.user = MagicMock(is_authenticated=True)

    with (
        patch(
            "codex_django.cabinet.views.site_settings.SiteSettingsService.save_context",
            return_value=(True, "Saved"),
        ),
        patch("codex_django.cabinet.views.site_settings.SiteSettingsService.get_context", return_value={}),
        patch("codex_django.cabinet.views.site_settings.render", return_value=HttpResponse("ok")),
    ):
        response = site_settings_view(request)

    assert response.status_code == 200
    assert any(m.message == "Saved" for m in messages)


@pytest.mark.unit
def test_site_settings_view_post_error():
    factory = RequestFactory()
    request = factory.post("/cabinet/site/settings/", data={"btn-save": "1"})

    request.session = MagicMock()
    messages = FallbackStorage(request)
    request._messages = messages
    request.user = MagicMock(is_authenticated=True)

    with (
        patch(
            "codex_django.cabinet.views.site_settings.SiteSettingsService.save_context",
            return_value=(False, "Failed"),
        ),
        patch("codex_django.cabinet.views.site_settings.SiteSettingsService.get_context", return_value={}),
        patch("codex_django.cabinet.views.site_settings.render", return_value=HttpResponse("ok")),
    ):
        response = site_settings_view(request)

    assert response.status_code == 200
    assert any(m.message == "Failed" for m in messages)
