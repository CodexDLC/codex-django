from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from django.test import override_settings

from codex_django.cabinet.redis.managers.dashboard import DashboardRedisManager


@pytest.fixture
def manager():
    with patch("codex_django.core.redis.managers.base.Redis.from_url", return_value=AsyncMock()):
        mgr = DashboardRedisManager()
    mgr._client = AsyncMock()
    return mgr


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dashboard_manager_aget_returns_deserialized_payload(manager):
    manager._client.get.return_value = '{"revenue":"10.50","count":2}'

    result = await manager.aget("kpi")

    assert result == {"revenue": "10.50", "count": 2}
    manager._client.get.assert_called_once_with(manager.make_key("kpi"))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dashboard_manager_aget_returns_none_for_invalid_json(manager):
    manager._client.get.return_value = "{bad json"

    assert await manager.aget("kpi") is None


@pytest.mark.unit
def test_dashboard_manager_set_serializes_decimal_payload(manager):
    manager.set("kpi", {"total": Decimal("99.50")}, ttl=300)

    manager._client.set.assert_called_once()
    args = manager._client.set.await_args.args
    assert args[0] == manager.make_key("kpi")
    assert args[1] == '{"total": "99.50"}'
    assert manager._client.set.await_args.kwargs == {"ex": 300}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dashboard_manager_invalidate_all_deletes_found_keys(manager):
    manager._client.keys.return_value = ["p1", "p2"]

    await manager.ainvalidate_all()

    manager._client.keys.assert_called_once_with(manager.make_key("*"))
    manager._client.delete.assert_called_once_with("p1", "p2")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dashboard_manager_disabled_in_debug_skips_reads(manager):
    with override_settings(DEBUG=True, CODEX_REDIS_ENABLED=False):
        assert await manager.aget("kpi") is None

    manager._client.get.assert_not_called()
