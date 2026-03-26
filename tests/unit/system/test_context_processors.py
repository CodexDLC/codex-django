"""
Unit tests for codex_django.system.context_processors
======================================================
All external dependencies (Redis, DB, apps) are mocked.
"""
from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory

from codex_django.system.context_processors import site_settings, static_content


@pytest.mark.unit
class TestSiteSettingsContextProcessor:
    """Tests for site_settings()."""

    @pytest.fixture
    def http_req(self):
        return RequestFactory().get("/")

    def test_no_setting_returns_empty_proxy(self, http_req):
        """When CODEX_SITE_SETTINGS_MODEL is not set, returns SettingsProxy({})."""
        with patch("codex_django.system.context_processors.settings") as mock_settings:
            mock_settings.CODEX_SITE_SETTINGS_MODEL = None
            result = site_settings(http_req)

        assert "site_settings" in result
        assert result["site_settings"].data == {}

    def test_returns_proxy_with_data_on_success(self, http_req):
        """When setting is present and manager returns data, returns SettingsProxy(data)."""
        fake_data = {"phone": "+1234567890", "email": "info@example.com"}

        mock_manager = MagicMock()
        mock_manager.load_cached.return_value = fake_data

        with (
            patch("codex_django.system.context_processors.settings") as mock_settings,
            patch("codex_django.system.context_processors.apps") as mock_apps,
            patch(
                "codex_django.system.context_processors.get_site_settings_manager",
                return_value=mock_manager,
            ),
        ):
            mock_settings.CODEX_SITE_SETTINGS_MODEL = "myapp.SiteSettings"
            mock_apps.get_model.return_value = MagicMock()

            result = site_settings(http_req)

        assert "site_settings" in result
        assert result["site_settings"].data == fake_data

    def test_exception_returns_empty_proxy(self, http_req):
        """When an exception is raised, returns SettingsProxy({}) and logs a warning."""
        with (
            patch("codex_django.system.context_processors.settings") as mock_settings,
            patch("codex_django.system.context_processors.apps") as mock_apps,
        ):
            mock_settings.CODEX_SITE_SETTINGS_MODEL = "myapp.SiteSettings"
            mock_apps.get_model.side_effect = Exception("model not found")

            result = site_settings(http_req)

        assert "site_settings" in result
        assert result["site_settings"].data == {}


@pytest.mark.unit
class TestStaticContentContextProcessor:
    """Tests for static_content()."""

    @pytest.fixture
    def http_req(self):
        return RequestFactory().get("/")

    def test_no_setting_returns_empty_dict(self, http_req):
        """When CODEX_STATIC_TRANSLATION_MODEL is not set, returns empty dict."""
        with patch("codex_django.system.context_processors.settings") as mock_settings:
            mock_settings.CODEX_STATIC_TRANSLATION_MODEL = None
            result = static_content(http_req)

        assert result == {"static_content": {}}

    def test_returns_key_content_mapping(self, http_req):
        """When setting present and objects exist, returns {key: content} dict."""
        obj1 = MagicMock(key="hero_title", content="Welcome!")
        obj2 = MagicMock(key="hero_subtitle", content="Best service ever.")

        mock_model = MagicMock()
        mock_model.objects.all.return_value = [obj1, obj2]

        with (
            patch("codex_django.system.context_processors.settings") as mock_settings,
            patch("codex_django.system.context_processors.apps") as mock_apps,
        ):
            mock_settings.CODEX_STATIC_TRANSLATION_MODEL = "myapp.StaticTranslation"
            mock_apps.get_model.return_value = mock_model

            result = static_content(http_req)

        assert result == {
            "static_content": {
                "hero_title": "Welcome!",
                "hero_subtitle": "Best service ever.",
            }
        }

    def test_exception_returns_empty_dict(self, http_req):
        """When an exception is raised, returns empty dict."""
        with (
            patch("codex_django.system.context_processors.settings") as mock_settings,
            patch("codex_django.system.context_processors.apps") as mock_apps,
        ):
            mock_settings.CODEX_STATIC_TRANSLATION_MODEL = "myapp.StaticTranslation"
            mock_apps.get_model.side_effect = Exception("DB error")

            result = static_content(http_req)

        assert result == {"static_content": {}}
