"""Unit tests for ``codex_django.sessions.backends.redis.SessionStore``.

All tests stub the Redis layer — no live Redis is required.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from codex_platform.redis_service.exceptions import RedisConnectionError
from django.contrib.sessions.backends.base import CreateError, UpdateError

from codex_django.sessions.backends.redis import SessionStore

pytestmark = [pytest.mark.unit]

VALID_KEY = "a" * 32


class MockStringOperations(AsyncMock):
    pass


class MockSyncStringOperations(MagicMock):
    pass


def _make_store(session_key: str | None = None) -> tuple[SessionStore, MockStringOperations, MockSyncStringOperations]:
    store = SessionStore(session_key)
    manager = MagicMock()

    async_s = MockStringOperations()
    async_ctx = AsyncMock()
    async_ctx.__aenter__.return_value = async_s
    manager.async_string.return_value = async_ctx

    sync_s = MockSyncStringOperations()
    sync_ctx = MagicMock()
    sync_ctx.__enter__.return_value = sync_s
    manager.sync_string.return_value = sync_ctx

    store._manager = manager
    return store, async_s, sync_s


# ---- keys --------------------------------------------------------------


def test_key_uses_project_name_and_session_prefix() -> None:
    store, _, _ = _make_store()
    assert store._key(VALID_KEY) == f"codex-django-test:session:{VALID_KEY}"


def test_key_prefix_override_from_settings(settings: Any) -> None:
    settings.CODEX_SESSION_KEY_PREFIX = "sess"
    settings.PROJECT_NAME = "test-proj"
    store, _, _ = _make_store()
    assert store._key(VALID_KEY) == f"test-proj:sess:{VALID_KEY}"


# ---- aexists -----------------------------------------------------------


@pytest.mark.asyncio
async def test_aexists_true() -> None:
    store, async_s, _ = _make_store()
    async_s.exists.return_value = True
    assert await store.aexists(VALID_KEY) is True
    async_s.exists.assert_awaited_once_with(store._key(VALID_KEY))


@pytest.mark.asyncio
async def test_aexists_false() -> None:
    store, async_s, _ = _make_store()
    async_s.exists.return_value = False
    assert await store.aexists(VALID_KEY) is False


def test_sync_exists_delegates_to_sync_manager() -> None:
    store, _, sync_s = _make_store()
    sync_s.exists.return_value = True
    assert store.exists(VALID_KEY) is True
    sync_s.exists.assert_called_once_with(store._key(VALID_KEY))


# ---- aload -------------------------------------------------------------


@pytest.mark.asyncio
async def test_aload_returns_empty_when_no_session_key() -> None:
    store, async_s, _ = _make_store()
    assert await store.aload() == {}
    async_s.get.assert_not_called()


@pytest.mark.asyncio
async def test_aload_returns_empty_on_missing_key() -> None:
    store, async_s, _ = _make_store(VALID_KEY)
    async_s.get.return_value = None
    assert await store.aload() == {}


@pytest.mark.asyncio
async def test_aload_decodes_payload() -> None:
    store, async_s, _ = _make_store(VALID_KEY)
    payload = store.encode({"uid": 42, "foo": "bar"})
    async_s.get.return_value = payload
    assert await store.aload() == {"uid": 42, "foo": "bar"}


@pytest.mark.asyncio
async def test_aload_returns_empty_on_corrupt_payload() -> None:
    store, async_s, _ = _make_store(VALID_KEY)
    async_s.get.return_value = "not-a-valid-signed-payload"
    assert await store.aload() == {}


# ---- asave -------------------------------------------------------------


@pytest.mark.asyncio
async def test_asave_must_create_uses_setnx_with_ttl() -> None:
    store, async_s, _ = _make_store(VALID_KEY)
    async_s.client.set = AsyncMock(return_value=True)
    await store.asave(must_create=True)
    async_s.client.set.assert_awaited_once()
    args, kwargs = async_s.client.set.call_args
    assert args[0] == store._key(VALID_KEY)
    assert kwargs["ex"] == store.get_expiry_age()
    assert kwargs["nx"] is True


@pytest.mark.asyncio
async def test_asave_must_create_collision_raises_create_error() -> None:
    store, async_s, _ = _make_store(VALID_KEY)
    async_s.client.set = AsyncMock(return_value=False)
    with pytest.raises(CreateError):
        await store.asave(must_create=True)
    async_s.set.assert_not_called()


@pytest.mark.asyncio
async def test_asave_update_missing_raises_update_error() -> None:
    store, async_s, _ = _make_store(VALID_KEY)
    async_s.exists.return_value = False
    with pytest.raises(UpdateError):
        await store.asave(must_create=False)
    async_s.set.assert_not_called()


@pytest.mark.asyncio
async def test_asave_update_existing_uses_set_with_ttl() -> None:
    store, async_s, _ = _make_store(VALID_KEY)
    async_s.exists.return_value = True
    await store.asave(must_create=False)
    async_s.set.assert_awaited_once()
    args, kwargs = async_s.set.call_args
    assert args[0] == store._key(VALID_KEY)
    assert kwargs["ttl"] == store.get_expiry_age()


@pytest.mark.asyncio
async def test_asave_without_session_key_creates_new_one() -> None:
    store, async_s, _ = _make_store()
    async_s.exists.return_value = False
    async_s.client.set = AsyncMock(return_value=True)
    await store.asave()
    assert store.session_key is not None
    async_s.client.set.assert_awaited_once()


# ---- adelete -----------------------------------------------------------


@pytest.mark.asyncio
async def test_adelete_uses_namespaced_key() -> None:
    store, async_s, _ = _make_store(VALID_KEY)
    await store.adelete()
    async_s.delete.assert_awaited_once_with(store._key(VALID_KEY))


@pytest.mark.asyncio
async def test_adelete_with_explicit_key() -> None:
    store, async_s, _ = _make_store()
    await store.adelete(VALID_KEY)
    async_s.delete.assert_awaited_once_with(store._key(VALID_KEY))


@pytest.mark.asyncio
async def test_adelete_noop_when_no_key() -> None:
    store, async_s, _ = _make_store()
    await store.adelete()
    async_s.delete.assert_not_called()


# ---- acreate -----------------------------------------------------------


@pytest.mark.asyncio
async def test_acreate_retries_on_collision() -> None:
    store, async_s, _ = _make_store()
    async_s.exists.return_value = False
    async_s.client.set = AsyncMock(side_effect=[False, True])
    await store.acreate()
    assert store.session_key is not None
    assert async_s.client.set.await_count == 2
    assert store.modified is True


# ---- redis errors propagate -------------------------------------------


@pytest.mark.asyncio
async def test_connection_error_not_swallowed_on_aexists() -> None:
    store, async_s, _ = _make_store()
    async_s.exists.side_effect = RedisConnectionError("down")
    with pytest.raises(RedisConnectionError):
        await store.aexists(VALID_KEY)


@pytest.mark.asyncio
async def test_connection_error_not_swallowed_on_aload() -> None:
    store, async_s, _ = _make_store(VALID_KEY)
    async_s.get.side_effect = RedisConnectionError("down")
    with pytest.raises(RedisConnectionError):
        await store.aload()


@pytest.mark.asyncio
async def test_connection_error_not_swallowed_on_asave() -> None:
    store, async_s, _ = _make_store(VALID_KEY)
    async_s.client.set = AsyncMock(side_effect=RedisConnectionError("down"))
    with pytest.raises(RedisConnectionError):
        await store.asave(must_create=True)


# ---- clear_expired is a no-op -----------------------------------------


def test_clear_expired_is_noop() -> None:
    assert SessionStore.clear_expired() is None


# ---- sync API ----------------------------------------------------------


def test_sync_load_save_and_delete_paths() -> None:
    store, _, sync_s = _make_store(VALID_KEY)
    payload = store.encode({"uid": 42})
    sync_s.get.return_value = payload
    assert store.load() == {"uid": 42}
    sync_s.get.assert_called_once_with(store._key(VALID_KEY))

    sync_s.exists.return_value = True
    store.save(must_create=False)
    sync_s.set.assert_called_once()
    args, kwargs = sync_s.set.call_args
    assert args[0] == store._key(VALID_KEY)
    assert kwargs["ttl"] == store.get_expiry_age()

    sync_s.client.set.return_value = True
    store.save(must_create=True)
    _, kwargs = sync_s.client.set.call_args
    assert kwargs["nx"] is True
    assert kwargs["ex"] == store.get_expiry_age()

    store.delete()
    sync_s.delete.assert_called_once_with(store._key(VALID_KEY))


def test_sync_create_retries_on_collision() -> None:
    store, _, sync_s = _make_store()
    sync_s.exists.return_value = False
    sync_s.client.set.side_effect = [False, True]

    store.create()

    assert store.session_key is not None
    assert sync_s.client.set.call_count == 2
    assert store.modified is True


def test_sync_save_update_missing_raises_update_error() -> None:
    store, _, sync_s = _make_store(VALID_KEY)
    sync_s.exists.return_value = False

    with pytest.raises(UpdateError):
        store.save(must_create=False)
