from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from django.test import override_settings

from codex_django.cabinet.redis.managers.dashboard import DashboardRedisManager


@pytest.fixture
def manager():
    mgr = DashboardRedisManager()

    async_string = AsyncMock()
    async_context = AsyncMock()
    async_context.__aenter__.return_value = async_string
    mgr.async_string = MagicMock(return_value=async_context)  # type: ignore[method-assign]

    sync_string = MagicMock()
    sync_context = MagicMock()
    sync_context.__enter__.return_value = sync_string
    mgr.sync_string = MagicMock(return_value=sync_context)  # type: ignore[method-assign]

    return mgr, async_string, sync_string


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dashboard_manager_aget_returns_deserialized_payload(manager):
    mgr, async_string, _ = manager
    async_string.get.return_value = '{"revenue":"10.50","count":2}'

    result = await mgr.aget("kpi")

    assert result == {"revenue": "10.50", "count": 2}
    async_string.get.assert_awaited_once_with(mgr.make_key("kpi"))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dashboard_manager_aget_returns_none_for_invalid_json(manager):
    mgr, async_string, _ = manager
    async_string.get.return_value = "{bad json"

    assert await mgr.aget("kpi") is None


@pytest.mark.unit
def test_dashboard_manager_set_serializes_decimal_payload(manager):
    mgr, _, sync_string = manager

    mgr.set("kpi", {"total": Decimal("99.50")}, ttl=300)

    sync_string.set.assert_called_once()
    args = sync_string.set.call_args.args
    assert args[0] == mgr.make_key("kpi")
    assert args[1] == '{"total": "99.50"}'
    assert sync_string.set.call_args.kwargs == {"ttl": 300}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dashboard_manager_invalidate_all_deletes_found_keys(manager):
    mgr, async_string, _ = manager

    await mgr.ainvalidate_all()

    async_string.delete_by_pattern.assert_awaited_once_with(mgr.make_key("*"))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dashboard_manager_disabled_in_debug_skips_reads(manager):
    mgr, async_string, _ = manager
    with override_settings(DEBUG=True, CODEX_REDIS_ENABLED=False):
        assert await mgr.aget("kpi") is None

    async_string.get.assert_not_called()


@pytest.mark.unit
def test_dashboard_manager_sync_get_and_invalidate_paths(manager):
    mgr, _, sync_string = manager
    sync_string.get.return_value = '{"revenue":"10.50","count":2}'

    assert mgr.get("kpi") == {"revenue": "10.50", "count": 2}
    sync_string.get.assert_called_once_with(mgr.make_key("kpi"))

    sync_string.get.return_value = "{bad json"
    assert mgr.get("kpi") is None

    mgr.invalidate("kpi")
    sync_string.delete.assert_called_once_with(mgr.make_key("kpi"))


@pytest.mark.unit
def test_dashboard_manager_sync_invalidate_all_deletes_found_keys(manager):
    mgr, _, _ = manager
    client = MagicMock()
    client.keys.return_value = ["p1", "p2"]
    mgr._sync_factory = MagicMock(return_value=client)  # type: ignore[method-assign]

    mgr.invalidate_all()

    client.keys.assert_called_once_with(mgr.make_key("*"))
    client.delete.assert_called_once_with("p1", "p2")
    client.close.assert_called_once()
