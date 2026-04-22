"""Unit tests for :class:`codex_django.cache.backends.redis.RedisCache`.

All Redis access is replaced with ``AsyncMock`` and ``MagicMock`` — no live Redis required.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from codex_platform.redis_service.exceptions import RedisConnectionError
from django.core.exceptions import ImproperlyConfigured

from codex_django.cache.backends.redis import RedisCache

pytestmark = [pytest.mark.unit]


class MockStringOperations(AsyncMock):
    pass


class MockSyncStringOperations(MagicMock):
    pass


def _make_cache(
    *,
    key_prefix: str = "codex",
    version: int = 1,
    default_timeout: int = 300,
    options: dict[str, Any] | None = None,
) -> tuple[RedisCache, MockStringOperations, MockSyncStringOperations]:
    params: dict[str, Any] = {
        "KEY_PREFIX": key_prefix,
        "VERSION": version,
        "TIMEOUT": default_timeout,
    }
    if options is not None:
        params["OPTIONS"] = options
    cache = RedisCache(server=None, params=params)

    manager = MagicMock()
    async_s = MockStringOperations()
    async_ctx = AsyncMock()
    async_ctx.__aenter__.return_value = async_s
    manager.async_string.return_value = async_ctx

    sync_s = MockSyncStringOperations()
    sync_ctx = MagicMock()
    sync_ctx.__enter__.return_value = sync_s
    manager.sync_string.return_value = sync_ctx

    cache._manager = manager
    return cache, async_s, sync_s


def _full_key(cache: RedisCache, key: str) -> str:
    return cache.make_key(key)


# ---- get / set --------------------------------------------------------


@pytest.mark.asyncio
async def test_set_and_get_roundtrip() -> None:
    cache, async_s, _ = _make_cache()
    async_s.get.return_value = '{"a":1}'
    await cache.aset("k", {"a": 1}, timeout=60)
    async_s.set.assert_awaited_once()
    args, kwargs = async_s.set.call_args
    assert args[0] == _full_key(cache, "k")
    assert args[1] == '{"a":1}'
    assert kwargs["ttl"] == 60

    assert await cache.aget("k") == {"a": 1}
    async_s.get.assert_awaited_once_with(_full_key(cache, "k"))


@pytest.mark.asyncio
async def test_get_returns_default_for_missing() -> None:
    cache, async_s, _ = _make_cache()
    async_s.get.return_value = None
    assert await cache.aget("missing", default="fallback") == "fallback"


@pytest.mark.asyncio
async def test_set_with_default_timeout_uses_default() -> None:
    cache, async_s, _ = _make_cache(default_timeout=42)
    await cache.aset("k", 1)
    _, kwargs = async_s.set.call_args
    assert kwargs["ttl"] == 42


@pytest.mark.asyncio
async def test_set_with_timeout_none_persists() -> None:
    cache, async_s, _ = _make_cache()
    await cache.aset("k", 1, timeout=None)
    _, kwargs = async_s.set.call_args
    assert kwargs.get("ttl") is None


@pytest.mark.asyncio
async def test_set_with_zero_timeout_deletes_instead() -> None:
    cache, async_s, _ = _make_cache()
    await cache.aset("k", 1, timeout=0)
    async_s.set.assert_not_called()
    async_s.delete.assert_awaited_once_with(_full_key(cache, "k"))


@pytest.mark.asyncio
async def test_set_negative_timeout_deletes() -> None:
    cache, async_s, _ = _make_cache()
    await cache.aset("k", 1, timeout=-5)
    async_s.delete.assert_awaited_once()


# ---- add --------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_returns_true_when_set() -> None:
    cache, async_s, _ = _make_cache()
    async_s.client.set = AsyncMock(return_value=True)
    assert await cache.aadd("k", 1, timeout=60) is True
    _, kwargs = async_s.client.set.call_args
    assert kwargs["ex"] == 60
    assert kwargs["nx"] is True


@pytest.mark.asyncio
async def test_add_returns_false_when_key_exists() -> None:
    cache, async_s, _ = _make_cache()
    async_s.client.set = AsyncMock(return_value=False)
    assert await cache.aadd("k", 1) is False


@pytest.mark.asyncio
async def test_add_with_zero_timeout_returns_false_without_call() -> None:
    cache, async_s, _ = _make_cache()
    assert await cache.aadd("k", 1, timeout=0) is False
    async_s.client.set.assert_not_called()


# ---- delete -----------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_returns_true_when_existed() -> None:
    cache, async_s, _ = _make_cache()
    async_s.exists.return_value = True
    assert await cache.adelete("k") is True
    async_s.delete.assert_awaited_once_with(_full_key(cache, "k"))


@pytest.mark.asyncio
async def test_delete_returns_false_when_missing() -> None:
    cache, async_s, _ = _make_cache()
    async_s.exists.return_value = False
    assert await cache.adelete("k") is False
    async_s.delete.assert_not_called()


# ---- has_key ----------------------------------------------------------


@pytest.mark.asyncio
async def test_has_key_true_false() -> None:
    cache, async_s, _ = _make_cache()
    async_s.exists.return_value = True
    assert await cache.ahas_key("k") is True
    async_s.exists.return_value = False
    assert await cache.ahas_key("k") is False


# ---- touch ------------------------------------------------------------


@pytest.mark.asyncio
async def test_touch_with_positive_ttl_calls_expire() -> None:
    cache, async_s, _ = _make_cache()
    async_s.expire.return_value = True
    assert await cache.atouch("k", timeout=120) is True
    async_s.expire.assert_awaited_once_with(_full_key(cache, "k"), 120)


@pytest.mark.asyncio
async def test_touch_with_none_ttl_calls_persist() -> None:
    cache, async_s, _ = _make_cache()
    async_s.client.persist = AsyncMock(return_value=True)
    assert await cache.atouch("k", timeout=None) is True
    async_s.client.persist.assert_awaited_once_with(_full_key(cache, "k"))


@pytest.mark.asyncio
async def test_touch_with_zero_timeout_deletes_and_reports_existence() -> None:
    cache, async_s, _ = _make_cache()
    async_s.exists.return_value = True
    assert await cache.atouch("k", timeout=0) is True
    async_s.delete.assert_awaited_once()


# ---- get_many / set_many / delete_many --------------------------------


@pytest.mark.asyncio
async def test_get_many_returns_only_found() -> None:
    cache, async_s, _ = _make_cache()
    async_s.mget.return_value = ['"a"', None, "42"]
    assert await cache.aget_many(["k1", "k2", "k3"]) == {"k1": "a", "k3": 42}


@pytest.mark.asyncio
async def test_set_many_calls_set_for_each() -> None:
    cache, async_s, _ = _make_cache()
    await cache.aset_many({"a": 1, "b": 2}, timeout=30)
    assert async_s.set.await_count == 2


@pytest.mark.asyncio
async def test_delete_many_iterates() -> None:
    cache, async_s, _ = _make_cache()
    async_s.exists.return_value = True
    await cache.adelete_many(["a", "b", "c"])
    assert async_s.delete.await_count == 3


# ---- incr / decr ------------------------------------------------------


@pytest.mark.asyncio
async def test_incr_raises_value_error_when_missing() -> None:
    cache, async_s, _ = _make_cache()
    async_s.exists.return_value = False
    with pytest.raises(ValueError):
        await cache.aincr("k")


@pytest.mark.asyncio
async def test_incr_calls_incrby() -> None:
    cache, async_s, _ = _make_cache()
    async_s.exists.return_value = True
    async_s.incr.return_value = 11
    assert await cache.aincr("k", delta=2) == 11
    async_s.incr.assert_awaited_once_with(_full_key(cache, "k"), 2)


@pytest.mark.asyncio
async def test_decr_negates_delta() -> None:
    cache, async_s, _ = _make_cache()
    async_s.exists.return_value = True
    async_s.incr.return_value = 8
    assert await cache.adecr("k", delta=3) == 8
    async_s.incr.assert_awaited_once_with(_full_key(cache, "k"), -3)


# ---- clear ------------------------------------------------------------


@pytest.mark.asyncio
async def test_clear_uses_namespaced_scan() -> None:
    cache, async_s, _ = _make_cache(key_prefix="codex")
    async_s.client.scan = AsyncMock(return_value=(0, [b"key1"]))
    async_s.client.delete = AsyncMock()
    await cache.aclear()
    async_s.client.scan.assert_awaited_once_with(cursor=0, match="codex:*", count=100)
    async_s.client.delete.assert_awaited_once_with(b"key1")


@pytest.mark.asyncio
async def test_clear_refuses_without_key_prefix() -> None:
    cache, _, _ = _make_cache(key_prefix="")
    with pytest.raises(ImproperlyConfigured):
        await cache.aclear()


# ---- error propagation ------------------------------------------------


@pytest.mark.asyncio
async def test_redis_connection_error_not_swallowed_on_get() -> None:
    cache, async_s, _ = _make_cache()
    async_s.get.side_effect = RedisConnectionError("down")
    with pytest.raises(RedisConnectionError):
        await cache.aget("k")


@pytest.mark.asyncio
async def test_redis_connection_error_not_swallowed_on_set() -> None:
    cache, async_s, _ = _make_cache()
    async_s.set.side_effect = RedisConnectionError("down")
    with pytest.raises(RedisConnectionError):
        await cache.aset("k", 1, timeout=60)


# ---- non-JSON payload -------------------------------------------------


@pytest.mark.asyncio
async def test_set_raises_type_error_on_non_json_value() -> None:
    cache, _, _ = _make_cache()
    with pytest.raises(TypeError):
        await cache.aset("k", {1, 2})


# ---- custom serializer via OPTIONS -----------------------------------


def test_options_serializer_is_loaded() -> None:
    cache, _, _ = _make_cache(
        options={"SERIALIZER": "codex_django.cache.serializers.JsonSerializer"},
    )
    assert cache._serializer.__class__.__name__ == "JsonSerializer"


def test_invalid_serializer_path_raises() -> None:
    with pytest.raises(ImproperlyConfigured):
        RedisCache(
            server=None,
            params={
                "KEY_PREFIX": "x",
                "VERSION": 1,
                "OPTIONS": {"SERIALIZER": "does.not.Exist"},
            },
        )


# ---- sync API ----------------------------------------------------------


def test_sync_get_set_add_and_delete_paths() -> None:
    cache, _, sync_s = _make_cache()
    sync_s.get.return_value = '{"a":1}'
    assert cache.get("k") == {"a": 1}
    sync_s.get.assert_called_with(_full_key(cache, "k"))

    cache.set("k", {"a": 1}, timeout=60)
    args, kwargs = sync_s.set.call_args
    assert args[0] == _full_key(cache, "k")
    assert args[1] == '{"a":1}'
    assert kwargs["ttl"] == 60

    cache.set("expired", 1, timeout=0)
    sync_s.delete.assert_called_with(_full_key(cache, "expired"))

    sync_s.client.set.return_value = True
    assert cache.add("new", 1, timeout=30) is True
    _, kwargs = sync_s.client.set.call_args
    assert kwargs == {"nx": True, "ex": 30}

    sync_s.exists.return_value = False
    assert cache.delete("missing") is False
    sync_s.exists.return_value = True
    assert cache.delete("present") is True
    sync_s.delete.assert_called_with(_full_key(cache, "present"))


def test_sync_many_touch_incr_and_clear_paths() -> None:
    cache, _, sync_s = _make_cache()
    sync_s.exists.return_value = True
    sync_s.expire.return_value = True
    assert cache.touch("k", timeout=120) is True
    sync_s.expire.assert_called_with(_full_key(cache, "k"), 120)

    sync_s.client.persist.return_value = True
    assert cache.touch("k", timeout=None) is True
    sync_s.client.persist.assert_called_with(_full_key(cache, "k"))

    assert cache.touch("k", timeout=0) is True
    sync_s.mget.return_value = ['"a"', None, "42"]
    assert cache.get_many(["k1", "k2", "k3"]) == {"k1": "a", "k3": 42}

    assert cache.set_many({"a": 1, "b": 2}, timeout=30) == []
    cache.delete_many(["a", "b"])
    assert sync_s.delete.call_count >= 3

    sync_s.incr.return_value = 11
    assert cache.incr("counter", delta=2) == 11
    assert cache.decr("counter", delta=3) == 11

    sync_s.client.scan.return_value = (0, [b"key1"])
    cache.clear()
    sync_s.client.scan.assert_called_with(cursor=0, match="codex:*", count=100)
    sync_s.client.delete.assert_called_with(b"key1")
