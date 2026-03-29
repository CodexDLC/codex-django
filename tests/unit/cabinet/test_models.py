"""Unit tests for CabinetSettings model."""

from __future__ import annotations

from unittest.mock import patch

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _mock_cabinet_settings_redis_sync():
    """Keep singleton model tests isolated from Redis-backed lifecycle hooks."""
    with patch("codex_django.cabinet.redis.managers.settings.CabinetSettingsRedisManager.save_instance"):
        yield


class TestCabinetSettingsSingleton:
    def test_save_enforces_pk1(self):
        from codex_django.cabinet.models.settings import CabinetSettings

        obj = CabinetSettings(cabinet_name="Test")
        obj.save()
        assert obj.pk == 1

    def test_load_creates_on_first_call(self):
        from codex_django.cabinet.models.settings import CabinetSettings

        assert CabinetSettings.objects.count() == 0
        obj = CabinetSettings.load()
        assert obj.pk == 1
        assert CabinetSettings.objects.count() == 1

    def test_load_returns_existing(self):
        from codex_django.cabinet.models.settings import CabinetSettings

        CabinetSettings(cabinet_name="Custom", pk=1).save()
        obj = CabinetSettings.load()
        assert obj.cabinet_name == "Custom"

    def test_load_idempotent(self):
        from codex_django.cabinet.models.settings import CabinetSettings

        CabinetSettings.load()
        CabinetSettings.load()
        assert CabinetSettings.objects.count() == 1

    def test_second_save_does_not_create_new_row(self):
        from codex_django.cabinet.models.settings import CabinetSettings

        obj = CabinetSettings.load()
        obj.cabinet_name = "Updated"
        obj.save()
        assert CabinetSettings.objects.count() == 1
        assert CabinetSettings.objects.get(pk=1).cabinet_name == "Updated"

    def test_delete_is_noop(self):
        from codex_django.cabinet.models.settings import CabinetSettings

        obj = CabinetSettings.load()
        obj.delete()
        assert CabinetSettings.objects.filter(pk=1).exists()


class TestCabinetSettingsToCabinetDict:
    def test_returns_cabinet_name(self):
        from codex_django.cabinet.models.settings import CabinetSettings

        obj = CabinetSettings(cabinet_name="My Cabinet", pk=1)
        d = obj.to_cabinet_dict()
        assert d["cabinet_name"] == "My Cabinet"

    def test_no_logo_excludes_logo_key(self):
        from codex_django.cabinet.models.settings import CabinetSettings

        obj = CabinetSettings(cabinet_name="X", pk=1)
        d = obj.to_cabinet_dict()
        assert "logo" not in d

    def test_str_representation(self):
        from codex_django.cabinet.models.settings import CabinetSettings

        obj = CabinetSettings(cabinet_name="My App", pk=1)
        assert str(obj) == "My App"
