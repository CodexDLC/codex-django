"""
Unit tests for:
  - codex_django.core.context_processors.seo_settings
  - codex_django.core.templatetags.codex_i18n.translate_url
"""

from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory

# ---------------------------------------------------------------------------
# core.context_processors.seo_settings
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSeoSettingsContextProcessor:
    """Tests for core.context_processors.seo_settings()."""

    @pytest.fixture
    def factory(self):
        return RequestFactory()

    def _make_request(self, url_name=None):
        request = RequestFactory().get("/")
        if url_name:
            request.resolver_match = MagicMock()
            request.resolver_match.url_name = url_name
        else:
            request.resolver_match = None
        return request

    def test_no_resolver_match_returns_empty_seo(self):
        from codex_django.core.context_processors import seo_settings

        request = self._make_request(url_name=None)
        result = seo_settings(request)
        assert result == {"seo": {}}

    def test_resolver_match_without_url_name_returns_empty_seo(self):
        from codex_django.core.context_processors import seo_settings

        request = RequestFactory().get("/")
        request.resolver_match = MagicMock()
        request.resolver_match.url_name = None

        result = seo_settings(request)
        assert result == {"seo": {}}

    def test_seo_found_returns_data(self):
        from codex_django.core.context_processors import seo_settings

        request = self._make_request(url_name="home")
        fake_seo = {"title": "Home Page", "description": "Welcome"}

        with patch(
            "codex_django.core.context_processors.get_static_page_seo",
            return_value=fake_seo,
        ):
            result = seo_settings(request)

        assert result == {"seo": fake_seo}

    def test_seo_not_found_returns_empty_dict(self):
        from codex_django.core.context_processors import seo_settings

        request = self._make_request(url_name="about")

        with patch(
            "codex_django.core.context_processors.get_static_page_seo",
            return_value=None,
        ):
            result = seo_settings(request)

        assert result == {"seo": {}}


# ---------------------------------------------------------------------------
# core.templatetags.codex_i18n.translate_url
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTranslateUrlTag:
    """Tests for the translate_url simple tag."""

    def _call_tag(self, context: dict, lang_code: str) -> str:
        from codex_django.core.templatetags.codex_i18n import translate_url

        return translate_url(context, lang_code)

    def test_no_request_in_context_returns_empty_string(self):
        result = self._call_tag({}, "en")
        assert result == ""

    def test_empty_path_returns_empty_string(self):
        request = MagicMock()
        request.path = ""
        result = self._call_tag({"request": request}, "en")
        assert result == ""

    def test_translates_path_using_django_translate_url(self):
        request = MagicMock()
        request.path = "/ru/about/"

        with patch(
            "codex_django.core.templatetags.codex_i18n.django_translate_url",
            return_value="/en/about/",
        ) as mock_translate:
            result = self._call_tag({"request": request}, "en")

        mock_translate.assert_called_once_with("/ru/about/", "en")
        assert result == "/en/about/"
