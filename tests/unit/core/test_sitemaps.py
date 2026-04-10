from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.sitemaps import Sitemap

from codex_django.core.sitemaps import BaseSitemap, StaticPagesSitemap


class MockItem:
    def get_absolute_url(self):
        return "/mock-url/"


@pytest.mark.unit
class TestBaseSitemap:
    @pytest.fixture
    def sitemap(self):
        return BaseSitemap()

    def test_languages(self, sitemap):
        with patch.object(settings, "LANGUAGES", [("en", "English"), ("ru", "Russian")]):
            assert sitemap.languages == ["en", "ru"]

    def test_get_domain_with_canonical(self, sitemap):
        with patch.object(settings, "CANONICAL_DOMAIN", "https://example.com"):
            assert sitemap.get_domain() == "example.com"

    def test_get_domain_default(self, sitemap):
        if hasattr(settings, "CANONICAL_DOMAIN"):
            with patch.object(settings, "CANONICAL_DOMAIN", "localhost"):
                assert sitemap.get_domain() == "localhost"
        else:
            assert sitemap.get_domain() == "localhost"

    def test_location_with_item_obj(self, sitemap):
        item = MockItem()
        assert sitemap.location(item) == "/mock-url/"

    def test_location_with_string_reverse(self, sitemap):
        with patch("codex_django.core.sitemaps.reverse", return_value="/home/") as mock_reverse:
            assert sitemap.location("home") == "/home/"
            mock_reverse.assert_called_with("home")

    def test_location_with_namespace(self, sitemap):
        from django.urls import NoReverseMatch

        def side_effect(name):
            if name == "main:home":
                return "/main/home/"
            raise NoReverseMatch()

        with (
            patch("codex_django.core.sitemaps.reverse", side_effect=side_effect),
            patch.object(settings, "SITEMAP_LOOKUP_NAMESPACES", ["main"]),
        ):
            assert sitemap.location("home") == "/main/home/"

    def test_get_urls_calls_super(self, sitemap):
        # We need to mock super().get_urls()
        # Since BaseSitemap inherits from Sitemap, we patch Sitemap.get_urls
        mock_urls = [{"item": "home", "location": "/home/"}]

        with (
            patch.object(Sitemap, "get_urls", return_value=mock_urls),
            patch.object(settings, "LANGUAGES", [("en", "English")]),
            patch.object(settings, "CANONICAL_DOMAIN", "example.com"),
            patch("codex_django.core.sitemaps.translation.override"),
            patch("codex_django.core.sitemaps.reverse", return_value="/home/"),
        ):
            urls = sitemap.get_urls()
            assert len(urls) == 1
            assert urls[0]["item"] == "home"

    def test_get_urls_attaches_alternates(self, sitemap):
        mock_urls = [{"item": "home", "location": "https://example.com/en/home/"}]

        with (
            patch.object(Sitemap, "get_urls", return_value=mock_urls),
            patch.object(settings, "LANGUAGES", [("en", "English"), ("de", "Deutsch")]),
            patch.object(settings, "LANGUAGE_CODE", "en"),
            patch.object(settings, "SITEMAP_DEFAULT_LANGUAGE", "de", create=True),
            patch.object(settings, "CANONICAL_DOMAIN", "https://example.com"),
            patch("codex_django.core.sitemaps.reverse", side_effect=lambda name: f"/{name}/"),
        ):
            urls = sitemap.get_urls()

        assert urls[0]["alternates"] == [
            {"lang_code": "en", "location": "https://example.com/home/"},
            {"lang_code": "de", "location": "https://example.com/home/"},
            {"lang_code": "x-default", "location": "https://example.com/home/"},
        ]

    def test_get_x_default_language_uses_sitemap_setting(self, sitemap):
        with patch.object(settings, "SITEMAP_DEFAULT_LANGUAGE", "de", create=True):
            assert sitemap.get_x_default_language() == "de"

    def test_static_pages_sitemap_items_from_settings(self):
        sitemap = StaticPagesSitemap()

        with patch.object(settings, "SITEMAP_STATIC_PAGES", ["home", "contacts"], create=True):
            assert sitemap.items() == ["home", "contacts"]
