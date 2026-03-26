"""
Unit tests for codex_django.core.seo.selectors.get_static_page_seo
====================================================================
All Redis and DB calls are mocked.
"""
from unittest.mock import MagicMock, patch

import pytest

from codex_django.core.seo.selectors import get_static_page_seo


@pytest.mark.unit
class TestGetStaticPageSeo:
    """Tests for get_static_page_seo()."""

    def _make_manager(self, cached_data=None):
        manager = MagicMock()
        manager.get_page.return_value = cached_data
        return manager

    def test_cache_hit_returns_cached_data_without_db(self):
        cached = {"title": "Home", "description": "Welcome"}
        manager = self._make_manager(cached_data=cached)

        with (
            patch("codex_django.core.seo.selectors.get_seo_redis_manager", return_value=manager),
            patch("codex_django.core.seo.selectors.apps") as mock_apps,
        ):
            result = get_static_page_seo("home")

        assert result == cached
        mock_apps.get_model.assert_not_called()

    def test_no_setting_returns_none(self):
        manager = self._make_manager(cached_data=None)

        with (
            patch("codex_django.core.seo.selectors.get_seo_redis_manager", return_value=manager),
            patch("codex_django.core.seo.selectors.settings") as mock_settings,
        ):
            mock_settings.CODEX_STATIC_PAGE_SEO_MODEL = None
            result = get_static_page_seo("home")

        assert result is None

    def test_db_miss_returns_none(self):
        manager = self._make_manager(cached_data=None)
        mock_model = MagicMock()
        mock_model.objects.filter.return_value.first.return_value = None

        with (
            patch("codex_django.core.seo.selectors.get_seo_redis_manager", return_value=manager),
            patch("codex_django.core.seo.selectors.settings") as mock_settings,
            patch("codex_django.core.seo.selectors.apps") as mock_apps,
        ):
            mock_settings.CODEX_STATIC_PAGE_SEO_MODEL = "myapp.StaticPageSeo"
            mock_apps.get_model.return_value = mock_model

            result = get_static_page_seo("home")

        assert result is None
        manager.set_page.assert_not_called()

    def test_db_hit_caches_and_returns_flat_data(self):
        manager = self._make_manager(cached_data=None)

        fake_obj = MagicMock()
        fake_obj.to_dict.return_value = {"title": "Home", "description": None}
        del fake_obj.to_dict  # Force usage of model_to_dict path
        fake_obj = MagicMock()
        fake_obj.to_dict.return_value = {"title": "Home", "extra": 42}

        mock_model = MagicMock()
        mock_model.objects.filter.return_value.first.return_value = fake_obj

        with (
            patch("codex_django.core.seo.selectors.get_seo_redis_manager", return_value=manager),
            patch("codex_django.core.seo.selectors.settings") as mock_settings,
            patch("codex_django.core.seo.selectors.apps") as mock_apps,
        ):
            mock_settings.CODEX_STATIC_PAGE_SEO_MODEL = "myapp.StaticPageSeo"
            mock_apps.get_model.return_value = mock_model

            result = get_static_page_seo("home")

        # flat_data: all values converted to strings
        assert result is not None
        assert result["title"] == "Home"
        assert result["extra"] == "42"
        manager.set_page.assert_called_once()

    def test_exception_during_db_query_returns_none(self):
        manager = self._make_manager(cached_data=None)

        with (
            patch("codex_django.core.seo.selectors.get_seo_redis_manager", return_value=manager),
            patch("codex_django.core.seo.selectors.settings") as mock_settings,
            patch("codex_django.core.seo.selectors.apps") as mock_apps,
        ):
            mock_settings.CODEX_STATIC_PAGE_SEO_MODEL = "myapp.StaticPageSeo"
            mock_apps.get_model.side_effect = Exception("DB is down")

            result = get_static_page_seo("home")

        assert result is None
