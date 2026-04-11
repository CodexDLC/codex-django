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
            assert instance.enabled is True
            mock_save.assert_called_once()


@pytest.mark.unit
@pytest.mark.django_db
def test_get_all_settings_fallback_to_db(settings):
    settings.CODEX_SITE_SETTINGS_MODEL = "system.SiteSettings"

    # Mock Redis manager to return empty {} (simulating miss or disabled)
    with (
        patch("codex_django.cabinet.redis.managers.settings.CabinetSettingsRedisManager.get", return_value={}),
        patch.object(SiteSettingsService, "get_model") as mock_get_model,
        patch("codex_django.cabinet.models.settings.CabinetSettings.load") as mock_cab_load,
    ):
        mock_instance = MagicMock()
        mock_instance.to_dict.return_value = {"phone": "123456"}

        mock_model = MagicMock()
        mock_model.objects.first.return_value = mock_instance
        mock_get_model.return_value = mock_model

        mock_cab_instance = MagicMock()
        mock_cab_instance.to_cabinet_dict.return_value = {"cabinet_name": "Test Cabinet"}
        mock_cab_load.return_value = mock_cab_instance

        settings_data = SiteSettingsService.get_all_settings()

        assert settings_data["phone"] == "123456"
        assert settings_data["cabinet_name"] == "Test Cabinet"
        assert "cabinet_name" in settings_data
        assert "phone" in settings_data
