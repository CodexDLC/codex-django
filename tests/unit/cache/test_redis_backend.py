"""Unit tests for :class:`codex_django.cache.backends.redis.RedisCache`.

All Redis access is replaced with ``AsyncMock`` — no live Redis required.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from codex_platform.redis_service.exceptions import RedisConnectionError
from django.core.exceptions import ImproperlyConfigured

from codex_django.cache.backends.redis import RedisCache

pytestmark = [pytest.mark.unit]


def _make_cache(
    *,
    key_prefix: str = "codex",
    version: int = 1,
    default_timeout: int = 300,
    options: dict[str, Any] | None = None,
) -> tuple[RedisCache, MagicMock]:
    params: dict[str, Any] = {
        "KEY_PREFIX": key_prefix,
        "VERSION": version,
        "TIMEOUT": default_timeout,
    }
    if options is not None:
        params["OPTIONS"] = options
    cache = RedisCache(server=None, params=params)
    service = MagicMock()
    service.string = AsyncMock()
    service.string.client = AsyncMock()
    cache._service = service
    return cache, service


def _full_key(cache: RedisCache, key: str) -> str:
    return cache.make_key(key)


# ---- get / set --------------------------------------------------------


def test_set_and_get_roundtrip() -> None:
    cache, service = _make_cache()
    service.string.get.return_value = '{"a":1}'
    cache.set("k", {"a": 1}, timeout=60)
    service.string.set.assert_awaited_once()
    args, kwargs = service.string.set.call_args
    assert args[0] == _full_key(cache, "k")
    assert args[1] == '{"a":1}'
    assert kwargs["ttl"] == 60

    assert cache.get("k") == {"a": 1}
    service.string.get.assert_awaited_once_with(_full_key(cache, "k"))


def test_get_returns_default_for_missing() -> None:
    cache, service = _make_cache()
    service.string.get.return_value = None
    assert cache.get("missing", default="fallback") == "fallback"


def test_set_with_default_timeout_uses_default() -> None:
    cache, service = _make_cache(default_timeout=42)
    cache.set("k", 1)
    _, kwargs = service.string.set.call_args
    assert kwargs["ttl"] == 42


def test_set_with_timeout_none_persists() -> None:
    cache, service = _make_cache()
    cache.set("k", 1, timeout=None)
    _, kwargs = service.string.set.call_args
    assert kwargs["ttl"] is None


def test_set_with_zero_timeout_deletes_instead() -> None:
    cache, service = _make_cache()
    cache.set("k", 1, timeout=0)
    service.string.set.assert_not_called()
    service.string.delete.assert_awaited_once_with(_full_key(cache, "k"))


def test_set_negative_timeout_deletes() -> None:
    cache, service = _make_cache()
    cache.set("k", 1, timeout=-5)
    service.string.delete.assert_awaited_once()


# ---- add --------------------------------------------------------------


def test_add_returns_true_when_set() -> None:
    cache, service = _make_cache()
    service.string.setnx.return_value = True
    assert cache.add("k", 1, timeout=60) is True
    _, kwargs = service.string.setnx.call_args
    assert kwargs["ttl"] == 60


def test_add_returns_false_when_key_exists() -> None:
    cache, service = _make_cache()
    service.string.setnx.return_value = False
    assert cache.add("k", 1) is False


def test_add_with_zero_timeout_returns_false_without_call() -> None:
    cache, service = _make_cache()
    assert cache.add("k", 1, timeout=0) is False
    service.string.setnx.assert_not_called()


# ---- delete -----------------------------------------------------------


def test_delete_returns_true_when_existed() -> None:
    cache, service = _make_cache()
    service.string.exists.return_value = True
    assert cache.delete("k") is True
    service.string.delete.assert_awaited_once_with(_full_key(cache, "k"))


def test_delete_returns_false_when_missing() -> None:
    cache, service = _make_cache()
    service.string.exists.return_value = False
    assert cache.delete("k") is False
    service.string.delete.assert_not_called()


# ---- has_key ----------------------------------------------------------


def test_has_key_true_false() -> None:
    cache, service = _make_cache()
    service.string.exists.return_value = True
    assert cache.has_key("k") is True
    service.string.exists.return_value = False
    assert cache.has_key("k") is False


# ---- touch ------------------------------------------------------------


def test_touch_with_positive_ttl_calls_expire() -> None:
    cache, service = _make_cache()
    service.string.expire.return_value = True
    assert cache.touch("k", timeout=120) is True
    service.string.expire.assert_awaited_once_with(_full_key(cache, "k"), 120)


def test_touch_with_none_ttl_calls_persist() -> None:
    cache, service = _make_cache()
    service.string.client.persist.return_value = True
    assert cache.touch("k", timeout=None) is True
    service.string.client.persist.assert_awaited_once_with(_full_key(cache, "k"))


def test_touch_with_zero_timeout_deletes_and_reports_existence() -> None:
    cache, service = _make_cache()
    service.string.exists.return_value = True
    assert cache.touch("k", timeout=0) is True
    service.string.delete.assert_awaited_once()


# ---- get_many / set_many / delete_many --------------------------------


def test_get_many_returns_only_found() -> None:
    cache, service = _make_cache()
    service.string.mget.return_value = ['"a"', None, "42"]
    assert cache.get_many(["k1", "k2", "k3"]) == {"k1": "a", "k3": 42}


def test_set_many_calls_set_for_each() -> None:
    cache, service = _make_cache()
    cache.set_many({"a": 1, "b": 2}, timeout=30)
    assert service.string.set.await_count == 2


def test_delete_many_iterates() -> None:
    cache, service = _make_cache()
    service.string.exists.return_value = True
    cache.delete_many(["a", "b", "c"])
    assert service.string.delete.await_count == 3


# ---- incr / decr ------------------------------------------------------


def test_incr_raises_value_error_when_missing() -> None:
    cache, service = _make_cache()
    service.string.exists.return_value = False
    with pytest.raises(ValueError):
        cache.incr("k")


def test_incr_calls_incrby() -> None:
    cache, service = _make_cache()
    service.string.exists.return_value = True
    service.string.incrby.return_value = 11
    assert cache.incr("k", delta=2) == 11
    service.string.incrby.assert_awaited_once_with(_full_key(cache, "k"), 2)


def test_decr_negates_delta() -> None:
    cache, service = _make_cache()
    service.string.exists.return_value = True
    service.string.incrby.return_value = 8
    assert cache.decr("k", delta=3) == 8
    service.string.incrby.assert_awaited_once_with(_full_key(cache, "k"), -3)


# ---- clear ------------------------------------------------------------


def test_clear_uses_namespaced_scan() -> None:
    cache, service = _make_cache(key_prefix="codex")
    cache.clear()
    service.string.delete_by_pattern.assert_awaited_once_with("codex:*")


def test_clear_refuses_without_key_prefix() -> None:
    cache, _ = _make_cache(key_prefix="")
    with pytest.raises(ImproperlyConfigured):
        cache.clear()


# ---- error propagation ------------------------------------------------


def test_redis_connection_error_not_swallowed_on_get() -> None:
    cache, service = _make_cache()
    service.string.get.side_effect = RedisConnectionError("down")
    with pytest.raises(RedisConnectionError):
        cache.get("k")


def test_redis_connection_error_not_swallowed_on_set() -> None:
    cache, service = _make_cache()
    service.string.set.side_effect = RedisConnectionError("down")
    with pytest.raises(RedisConnectionError):
        cache.set("k", 1, timeout=60)


# ---- non-JSON payload -------------------------------------------------


def test_set_raises_type_error_on_non_json_value() -> None:
    cache, _ = _make_cache()
    with pytest.raises(TypeError):
        cache.set("k", {1, 2})  # set is not JSON-native


# ---- custom serializer via OPTIONS -----------------------------------


def test_options_serializer_is_loaded() -> None:
    cache, service = _make_cache(
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
