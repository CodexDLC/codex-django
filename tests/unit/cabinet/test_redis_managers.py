"""Unit tests for CabinetSettingsRedisManager."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from codex_django.cabinet.redis.managers.settings import CabinetSettingsRedisManager


@pytest.fixture
def mock_redis_from_url():
    """Prevent actual Redis connection during unit tests."""
    with patch("codex_django.core.redis.managers.base.Redis.from_url", return_value=AsyncMock()):
        yield


@pytest.fixture
def mgr(mock_redis_from_url):
    m = CabinetSettingsRedisManager()
    m.hash = AsyncMock()
    m.string = AsyncMock()
    return m


@pytest.mark.unit
class TestCabinetSettingsRedisManagerKey:
    def test_key_is_site_settings(self, mgr):
        key = mgr.make_key("site_settings")
        assert key.endswith("site_settings")
        assert "cabinet" not in key

    def test_key_contains_project_name(self, mgr):
        key = mgr.make_key("settings")
        assert "codex-django-test" in key  # from tests/settings.py PROJECT_NAME


@pytest.mark.unit
class TestCabinetSettingsRedisManagerGet:
    @pytest.mark.asyncio
    async def test_aget_returns_hash_data(self, mgr):
        mgr.hash.get_all.return_value = {"cabinet_name": "My Cabinet"}
        result = await mgr.aget()
        assert result == {"cabinet_name": "My Cabinet"}

    @pytest.mark.asyncio
    async def test_aget_returns_empty_dict_on_miss(self, mgr):
        mgr.hash.get_all.return_value = None
        result = await mgr.aget()
        assert result == {}

    def test_get_sync_wrapper(self, mgr):
        mgr.hash.get_all.return_value = {"cabinet_name": "Sync Test"}
        result = mgr.get()
        assert result == {"cabinet_name": "Sync Test"}

    def test_disabled_in_debug_returns_empty(self, mock_redis_from_url):
        """DEBUG=True + no CODEX_REDIS_ENABLED → returns {} without touching Redis."""
        from django.test import override_settings

        with override_settings(DEBUG=True, CODEX_REDIS_ENABLED=False):
            m = CabinetSettingsRedisManager()
            m.hash = AsyncMock()
            result = m.get()
        assert result == {}
        m.hash.get_all.assert_not_called()


@pytest.mark.unit
class TestCabinetSettingsRedisManagerSave:
    @pytest.mark.asyncio
    async def test_asave_instance_calls_set_fields(self, mgr):
        instance = MagicMock()
        instance.to_cabinet_dict.return_value = {"cabinet_name": "Cabinet"}
        await mgr.asave_instance(instance)
        mgr.hash.set_fields.assert_called_once_with(mgr.make_key("site_settings"), {"cabinet_name": "Cabinet"})

    @pytest.mark.asyncio
    async def test_asave_instance_skips_empty_dict(self, mgr):
        instance = MagicMock()
        instance.to_cabinet_dict.return_value = {}
        await mgr.asave_instance(instance)
        mgr.hash.set_fields.assert_not_called()

    def test_save_instance_sync_wrapper(self, mgr):
        instance = MagicMock()
        instance.to_cabinet_dict.return_value = {"cabinet_name": "Cabinet"}
        mgr.save_instance(instance)
        mgr.hash.set_fields.assert_called_once()

    def test_disabled_in_debug_save_skipped(self, mock_redis_from_url):
        from django.test import override_settings

        with override_settings(DEBUG=True, CODEX_REDIS_ENABLED=False):
            m = CabinetSettingsRedisManager()
            m.hash = AsyncMock()
            instance = MagicMock()
            instance.to_cabinet_dict.return_value = {"cabinet_name": "X"}
            m.save_instance(instance)
        m.hash.set_fields.assert_not_called()


@pytest.mark.unit
class TestCabinetSettingsRedisManagerInvalidate:
    @pytest.mark.asyncio
    async def test_ainvalidate_deletes_key(self, mgr):
        await mgr.ainvalidate()
        mgr.string.delete.assert_called_once_with(mgr.make_key("site_settings"))

    def test_invalidate_sync_wrapper(self, mgr):
        mgr.invalidate()
        mgr.string.delete.assert_called_once()

    def test_disabled_in_debug_invalidate_skipped(self, mock_redis_from_url):
        from django.test import override_settings

        with override_settings(DEBUG=True, CODEX_REDIS_ENABLED=False):
            m = CabinetSettingsRedisManager()
            m.string = AsyncMock()
            m.invalidate()
        m.string.delete.assert_not_called()
