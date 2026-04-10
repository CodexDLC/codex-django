from unittest.mock import MagicMock, patch

import pytest

from codex_django.cabinet.services.site_settings import SiteSettingsService


@pytest.mark.unit
def test_get_context():
    with patch(
        "codex_django.cabinet.redis.managers.settings.CabinetSettingsRedisManager.get",
        return_value={"staff_quick_access_links": "1,2"},
    ):
        request = MagicMock()
        # Mock get_tabs to avoid filesystem scan
        with patch.object(SiteSettingsService, "get_tabs", return_value=[]):
            ctx = SiteSettingsService.get_context(request)
            assert "tabs" in ctx
            assert ctx["settings_data"] == {"staff_quick_access_links": "1,2"}


@pytest.mark.unit
def test_site_settings_permission_hook_defaults_to_authenticated_user():
    user = MagicMock(is_authenticated=True)
    assert SiteSettingsService.user_can_access(user) is True


@pytest.mark.unit
def test_site_settings_hooks_are_overridable():
    class CustomService(SiteSettingsService):
        model_setting_name = "CUSTOM_SITE_SETTINGS_MODEL"
        excluded_post_fields = ("csrfmiddlewaretoken", "ignore-me")

        @classmethod
        def iter_tab_template_dirs(cls):
            return []

    assert CustomService.get_excluded_post_fields() == ("csrfmiddlewaretoken", "ignore-me")
    assert CustomService.get_tabs() == []


@pytest.mark.unit
@pytest.mark.django_db
def test_save_context_success(settings):
    request = MagicMock()
    request.POST.dict.return_value = {"enabled": "on"}
    settings.CODEX_SITE_SETTINGS_MODEL = "system.SiteSettings"

    with patch("django.apps.apps.get_model") as mock_get_model:

        class Instance:
            def __init__(self):
                self.enabled = False
                self._meta = MagicMock()

            def save(self):
                pass

        instance = Instance()
        from django.db import models

        field = models.BooleanField(name="enabled")
        field.concrete = True
        instance._meta.get_fields.return_value = [field]

        mock_model = MagicMock()
        mock_model.objects.first.return_value = instance
        mock_get_model.return_value = mock_model

        with patch.object(instance, "save") as mock_save:
            success, msg = SiteSettingsService.save_context(request)
            assert success is True, f"Failed with message: {msg}"
            assert instance.enabled is True
            mock_save.assert_called_once()
