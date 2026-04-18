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

VALID_KEY = "a" * 32  # SessionBase validates session_key format (alnum, 8+ chars).


def _make_store(session_key: str | None = None) -> tuple[SessionStore, MagicMock]:
    """Return a ``SessionStore`` with a fully mocked Redis service."""
    store = SessionStore(session_key)
    service = MagicMock()
    service.string = AsyncMock()
    store._service = service
    return store, service


# ---- keys --------------------------------------------------------------


def test_key_uses_project_name_and_session_prefix() -> None:
    store, _ = _make_store()
    assert store._key(VALID_KEY) == f"codex-django-test:session:{VALID_KEY}"


def test_key_prefix_override_from_settings(settings: Any) -> None:
    settings.CODEX_SESSION_KEY_PREFIX = "sess"
    store, _ = _make_store()
    assert store._key(VALID_KEY) == f"codex-django-test:sess:{VALID_KEY}"


# ---- aexists -----------------------------------------------------------


@pytest.mark.asyncio
async def test_aexists_true() -> None:
    store, service = _make_store()
    service.string.exists.return_value = True
    assert await store.aexists(VALID_KEY) is True
    service.string.exists.assert_awaited_once_with(store._key(VALID_KEY))


@pytest.mark.asyncio
async def test_aexists_false() -> None:
    store, service = _make_store()
    service.string.exists.return_value = False
    assert await store.aexists(VALID_KEY) is False


def test_sync_exists_delegates_to_async() -> None:
    store, service = _make_store()
    service.string.exists.return_value = True
    assert store.exists(VALID_KEY) is True
    service.string.exists.assert_awaited_once()


# ---- aload -------------------------------------------------------------


@pytest.mark.asyncio
async def test_aload_returns_empty_when_no_session_key() -> None:
    store, service = _make_store()
    assert await store.aload() == {}
    service.string.get.assert_not_called()


@pytest.mark.asyncio
async def test_aload_returns_empty_on_missing_key() -> None:
    store, service = _make_store(VALID_KEY)
    service.string.get.return_value = None
    assert await store.aload() == {}


@pytest.mark.asyncio
async def test_aload_decodes_payload() -> None:
    store, service = _make_store(VALID_KEY)
    payload = store.encode({"uid": 42, "foo": "bar"})
    service.string.get.return_value = payload
    assert await store.aload() == {"uid": 42, "foo": "bar"}


@pytest.mark.asyncio
async def test_aload_returns_empty_on_corrupt_payload() -> None:
    store, service = _make_store(VALID_KEY)
    service.string.get.return_value = "not-a-valid-signed-payload"
    assert await store.aload() == {}


# ---- asave -------------------------------------------------------------


@pytest.mark.asyncio
async def test_asave_must_create_uses_setnx_with_ttl() -> None:
    store, service = _make_store(VALID_KEY)
    service.string.setnx.return_value = True
    await store.asave(must_create=True)
    service.string.setnx.assert_awaited_once()
    args, kwargs = service.string.setnx.call_args
    assert args[0] == store._key(VALID_KEY)
    assert kwargs["ttl"] == store.get_expiry_age()


@pytest.mark.asyncio
async def test_asave_must_create_collision_raises_create_error() -> None:
    store, service = _make_store(VALID_KEY)
    service.string.setnx.return_value = False
    with pytest.raises(CreateError):
        await store.asave(must_create=True)
    service.string.set.assert_not_called()


@pytest.mark.asyncio
async def test_asave_update_missing_raises_update_error() -> None:
    store, service = _make_store(VALID_KEY)
    service.string.exists.return_value = False
    with pytest.raises(UpdateError):
        await store.asave(must_create=False)
    service.string.set.assert_not_called()


@pytest.mark.asyncio
async def test_asave_update_existing_uses_set_with_ttl() -> None:
    store, service = _make_store(VALID_KEY)
    service.string.exists.return_value = True
    await store.asave(must_create=False)
    service.string.set.assert_awaited_once()
    args, kwargs = service.string.set.call_args
    assert args[0] == store._key(VALID_KEY)
    assert kwargs["ttl"] == store.get_expiry_age()


@pytest.mark.asyncio
async def test_asave_without_session_key_creates_new_one() -> None:
    store, service = _make_store()
    service.string.exists.return_value = False  # fresh key → aexists False
    service.string.setnx.return_value = True
    await store.asave()
    assert store.session_key is not None
    service.string.setnx.assert_awaited_once()


# ---- adelete -----------------------------------------------------------


@pytest.mark.asyncio
async def test_adelete_uses_namespaced_key() -> None:
    store, service = _make_store(VALID_KEY)
    await store.adelete()
    service.string.delete.assert_awaited_once_with(store._key(VALID_KEY))


@pytest.mark.asyncio
async def test_adelete_with_explicit_key() -> None:
    store, service = _make_store()
    await store.adelete(VALID_KEY)
    service.string.delete.assert_awaited_once_with(store._key(VALID_KEY))


@pytest.mark.asyncio
async def test_adelete_noop_when_no_key() -> None:
    store, service = _make_store()
    await store.adelete()
    service.string.delete.assert_not_called()


# ---- acreate -----------------------------------------------------------


@pytest.mark.asyncio
async def test_acreate_retries_on_collision() -> None:
    store, service = _make_store()
    service.string.exists.return_value = False  # key free during _aget_new_session_key
    service.string.setnx.side_effect = [False, True]
    await store.acreate()
    assert store.session_key is not None
    assert service.string.setnx.await_count == 2
    assert store.modified is True


# ---- redis errors propagate -------------------------------------------


@pytest.mark.asyncio
async def test_connection_error_not_swallowed_on_aexists() -> None:
    store, service = _make_store()
    service.string.exists.side_effect = RedisConnectionError("down")
    with pytest.raises(RedisConnectionError):
        await store.aexists(VALID_KEY)


@pytest.mark.asyncio
async def test_connection_error_not_swallowed_on_aload() -> None:
    store, service = _make_store(VALID_KEY)
    service.string.get.side_effect = RedisConnectionError("down")
    with pytest.raises(RedisConnectionError):
        await store.aload()


@pytest.mark.asyncio
async def test_connection_error_not_swallowed_on_asave() -> None:
    store, service = _make_store(VALID_KEY)
    service.string.setnx.side_effect = RedisConnectionError("down")
    with pytest.raises(RedisConnectionError):
        await store.asave(must_create=True)


# ---- clear_expired is a no-op -----------------------------------------


def test_clear_expired_is_noop() -> None:
    assert SessionStore.clear_expired() is None
