"""
Unit tests for codex_django.system.mixins
==========================================
Imports from individual submodules (not __init__) to avoid
encrypted_model_fields loading when it's not under test.
"""
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# SiteSettingsSyncMixin — to_dict() and sync_to_redis()
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSiteSettingsSyncMixin:
    """Tests for to_dict() and sync_to_redis()."""

    def _make_instance(self):
        """Build an in-memory SiteSettingsSyncMixin instance with faked _meta."""
        from django.db import models

        # Import directly from submodule, not from __init__ (avoids encrypted_model_fields)
        from codex_django.system.mixins.settings import SiteSettingsSyncMixin

        obj = SiteSettingsSyncMixin.__new__(SiteSettingsSyncMixin)

        # Fake concrete CharField fields
        field_id = MagicMock(spec=models.AutoField)
        field_id.concrete = True
        field_id.many_to_many = False
        field_id.one_to_many = False
        field_id.name = "id"

        field_phone = MagicMock(spec=models.CharField)
        field_phone.concrete = True
        field_phone.many_to_many = False
        field_phone.one_to_many = False
        field_phone.name = "phone"

        field_email = MagicMock(spec=models.EmailField)
        field_email.concrete = True
        field_email.many_to_many = False
        field_email.one_to_many = False
        field_email.name = "email"

        obj._meta = MagicMock()
        obj._meta.get_fields.return_value = [field_id, field_phone, field_email]

        obj.phone = "+1234567890"
        obj.email = "test@example.com"
        return obj

    def test_to_dict_excludes_id(self):
        obj = self._make_instance()
        data = obj.to_dict()
        assert "id" not in data

    def test_to_dict_includes_concrete_fields(self):
        obj = self._make_instance()
        data = obj.to_dict()
        assert data["phone"] == "+1234567890"
        assert data["email"] == "test@example.com"

    def test_sync_to_redis_skipped_in_debug_mode(self):
        obj = self._make_instance()
        # settings is imported lazily INSIDE sync_to_redis(), so patch at the canonical location
        with (
            patch("django.conf.settings") as mock_settings,
            patch("codex_django.core.redis.managers.settings.get_site_settings_manager") as mock_get_mgr,
        ):
            mock_settings.DEBUG = True
            mock_settings.CODEX_REDIS_ENABLED = False
            obj.sync_to_redis()
            mock_get_mgr.assert_not_called()

    def test_sync_to_redis_calls_manager_when_not_debug(self):
        obj = self._make_instance()
        mock_manager = MagicMock()
        # settings is imported lazily INSIDE sync_to_redis(), so patch at django.conf level
        # get_site_settings_manager is also imported lazily inside sync_to_redis()
        with (
            patch("django.conf.settings") as mock_settings,
            patch(
                "codex_django.core.redis.managers.settings.get_site_settings_manager",
                return_value=mock_manager,
            ),
        ):
            mock_settings.DEBUG = False
            obj.sync_to_redis()
        mock_manager.save_instance.assert_called_once_with(obj)


# ---------------------------------------------------------------------------
# AbstractStaticPageSeo — save() invalidates cache
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAbstractStaticPageSeo:
    def test_save_invalidates_seo_cache(self):
        # Import directly from submodule
        from codex_django.system.mixins.seo import AbstractStaticPageSeo

        obj = AbstractStaticPageSeo.__new__(AbstractStaticPageSeo)
        obj.page_key = "home"

        mock_manager = MagicMock()

        with (
            patch("codex_django.system.mixins.seo.get_seo_redis_manager", return_value=mock_manager),
            patch("codex_django.system.mixins.seo.TimestampMixin.save"),
        ):
            obj.save()

        mock_manager.invalidate_page.assert_called_once_with("home")


# ---------------------------------------------------------------------------
# AbstractUserProfile — get_full_name() / get_initials()
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAbstractUserProfile:
    def _make_profile(self, first: str = "", last: str = "", patronymic: str = ""):
        # Import directly from submodule (not __init__)
        from codex_django.system.mixins.user_profile import AbstractUserProfile

        obj = AbstractUserProfile.__new__(AbstractUserProfile)
        obj.first_name = first
        obj.last_name = last
        obj.patronymic = patronymic
        return obj

    def test_get_full_name_all_parts(self):
        p = self._make_profile("John", "Doe", "Arthur")
        assert p.get_full_name() == "Doe John Arthur"

    def test_get_full_name_only_first_last(self):
        p = self._make_profile("John", "Doe")
        assert p.get_full_name() == "Doe John"

    def test_get_full_name_empty(self):
        p = self._make_profile()
        assert p.get_full_name() == ""

    def test_get_initials_two_letters(self):
        p = self._make_profile(first="John", last="Doe")
        assert p.get_initials() == "JD"

    def test_get_initials_only_first(self):
        p = self._make_profile(first="John")
        assert p.get_initials() == "J"

    def test_get_initials_empty_returns_question_mark(self):
        p = self._make_profile()
        assert p.get_initials() == "?"


# ---------------------------------------------------------------------------
# AbstractStaticTranslation — __str__()
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAbstractStaticTranslation:
    def test_str_returns_key(self):
        # Import directly from submodule (not __init__)
        from codex_django.system.mixins.translations import AbstractStaticTranslation

        obj = AbstractStaticTranslation.__new__(AbstractStaticTranslation)
        obj.key = "hero_title"
        assert str(obj) == "hero_title"
