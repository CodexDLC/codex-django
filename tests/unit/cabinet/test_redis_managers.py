"""Unit tests for CabinetSettingsRedisManager."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from codex_django.cabinet.redis.managers.settings import CabinetSettingsRedisManager


@pytest.fixture
def mgr():
    mgr = CabinetSettingsRedisManager()
    # Mock context managers
    mgr.async_hash = MagicMock()
    mgr.async_string = MagicMock()
    mgr.sync_hash = MagicMock()
    mgr.sync_string = MagicMock()

    # Separate mocks for async and sync operations
    mgr.hash = AsyncMock()
    mgr.string = AsyncMock()
    mgr.hash_sync = MagicMock()
    mgr.string_sync = MagicMock()

    # Configure context managers
    mgr.async_hash.return_value.__aenter__.return_value = mgr.hash
    mgr.async_string.return_value.__aenter__.return_value = mgr.string
    mgr.sync_hash.return_value.__enter__.return_value = mgr.hash_sync
    mgr.sync_string.return_value.__enter__.return_value = mgr.string_sync

    return mgr


@pytest.mark.unit
class TestCabinetSettingsRedisManagerKey:
    def test_key_is_site_settings(self, mgr):
        key = mgr.make_key("site_settings")
        assert key.endswith("site_settings")
        assert "cabinet" not in key

    def test_key_contains_project_name(self, settings):
        settings.PROJECT_NAME = "project"
        mgr = CabinetSettingsRedisManager()
        key = mgr.make_key("settings")
        assert "project" in key


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
        mgr.hash_sync.get_all.return_value = {"cabinet_name": "Sync Test"}
        result = mgr.get()
        assert result == {"cabinet_name": "Sync Test"}

    def test_disabled_in_debug_returns_empty(self, settings):
        """DEBUG=True + no CODEX_REDIS_ENABLED → returns {} without touching Redis."""
        settings.DEBUG = True
        settings.CODEX_REDIS_ENABLED = False

        m = CabinetSettingsRedisManager()
        m.sync_hash = MagicMock()
        result = m.get()
        assert result == {}
        m.sync_hash.assert_not_called()


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
        mgr.hash_sync.set_fields.assert_called_once()

    def test_disabled_in_debug_save_skipped(self, settings):
        settings.DEBUG = True
        settings.CODEX_REDIS_ENABLED = False

        m = CabinetSettingsRedisManager()
        m.sync_hash = MagicMock()
        instance = MagicMock()
        instance.to_cabinet_dict.return_value = {"cabinet_name": "X"}
        m.save_instance(instance)
        m.sync_hash.assert_not_called()


@pytest.mark.unit
class TestCabinetSettingsRedisManagerInvalidate:
    @pytest.mark.asyncio
    async def test_ainvalidate_deletes_key(self, mgr):
        await mgr.ainvalidate()
        mgr.string.delete.assert_called_once_with(mgr.make_key("site_settings"))

    def test_invalidate_sync_wrapper(self, mgr):
        mgr.invalidate()
        mgr.string_sync.delete.assert_called_once_with(mgr.make_key("site_settings"))

    def test_disabled_in_debug_invalidate_skipped(self, settings):
        settings.DEBUG = True
        settings.CODEX_REDIS_ENABLED = False

        m = CabinetSettingsRedisManager()
        m.sync_string = MagicMock()
        m.invalidate()
        m.sync_string.assert_not_called()
