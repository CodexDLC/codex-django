from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis

from codex_django.core.redis.managers.base import BaseDjangoRedisManager


@pytest.fixture
def mock_async_client() -> AsyncMock:
    client = AsyncMock(spec=AsyncRedis)
    return client


@pytest.fixture
def mock_sync_client() -> MagicMock:
    client = MagicMock(spec=SyncRedis)
    return client


@pytest.fixture
def manager(mock_async_client: AsyncMock, mock_sync_client: MagicMock) -> BaseDjangoRedisManager:
    return BaseDjangoRedisManager(
        async_client_factory=lambda: mock_async_client,
        sync_client_factory=lambda: mock_sync_client,
    )


def test_default_factories() -> None:
    # default factories are assigned if none provided
    mgr = BaseDjangoRedisManager()
    with patch("redis.asyncio.Redis.from_url") as mock_async_from_url:
        mgr._async_factory()
        mock_async_from_url.assert_called_once_with(mgr._redis_url, decode_responses=True)

    with patch("redis.Redis.from_url") as mock_sync_from_url:
        mgr._sync_factory()
        mock_sync_from_url.assert_called_once_with(mgr._redis_url, decode_responses=True)


@pytest.mark.asyncio
async def test_async_string_context_manager(manager: BaseDjangoRedisManager, mock_async_client: AsyncMock) -> None:
    async with manager.async_string() as s:
        assert s.client == mock_async_client
    mock_async_client.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_hash_context_manager(manager: BaseDjangoRedisManager, mock_async_client: AsyncMock) -> None:
    async with manager.async_hash() as h:
        assert h.client == mock_async_client
    mock_async_client.aclose.assert_awaited_once()


def test_sync_string_context_manager(manager: BaseDjangoRedisManager, mock_sync_client: MagicMock) -> None:
    with manager.sync_string() as s:
        assert s.client == mock_sync_client
    mock_sync_client.close.assert_called_once()


def test_sync_hash_context_manager(manager: BaseDjangoRedisManager, mock_sync_client: MagicMock) -> None:
    with manager.sync_hash() as h:
        assert h.client == mock_sync_client
    mock_sync_client.close.assert_called_once()
