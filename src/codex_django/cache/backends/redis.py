"""Redis-backed Django cache backend (JSON, no pickle).

Wire this up as::

    CACHES = {
        "default": {
            "BACKEND": "codex_django.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,       # optional; falls back to settings.REDIS_URL
            "KEY_PREFIX": PROJECT_NAME,  # required for clear() to be namespace-scoped
            "TIMEOUT": 300,
            "OPTIONS": {
                # Optional: "SERIALIZER": "my_app.cache.CustomSerializer",
            },
        }
    }

Design highlights:

* Values are stored as UTF-8 JSON strings (see
  :mod:`codex_django.cache.serializers`). Non-JSON-native values raise
  ``TypeError``; there is no pickle fallback.
* ``add`` uses Redis ``SET NX EX`` atomically.
* ``clear`` uses ``SCAN + DEL`` scoped to ``{key_prefix}:*``. If
  ``KEY_PREFIX`` is empty, ``clear`` refuses to run — **never** ``FLUSHDB``.
* Redis errors propagate to the caller as
  :class:`codex_platform.redis_service.exceptions.RedisConnectionError` /
  ``RedisServiceError`` — the cache does not silently degrade.
"""

from __future__ import annotations

from collections.abc import Iterable
from importlib import import_module
from typing import Any

from asgiref.sync import async_to_sync
from django.core.cache.backends.base import DEFAULT_TIMEOUT, BaseCache
from django.core.exceptions import ImproperlyConfigured

from codex_django.cache.serializers import JsonSerializer, Serializer
from codex_django.core.redis.django_adapter import build_redis_service

_UNSET = object()


def _import_serializer(dotted: str) -> Serializer:
    module_path, _, class_name = dotted.rpartition(".")
    if not module_path:
        raise ImproperlyConfigured(f"Invalid SERIALIZER path: {dotted!r}")
    try:
        module = import_module(module_path)
        cls = getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        raise ImproperlyConfigured(f"Cannot import serializer {dotted!r}: {exc}") from exc
    return cls()  # type: ignore[no-any-return]


class RedisCache(BaseCache):
    """Django cache backend that stores JSON strings in Redis."""

    def __init__(self, server: str | None, params: dict[str, Any]) -> None:
        super().__init__(params)
        self._location = server or None
        options = params.get("OPTIONS") or {}
        serializer_path = options.get("SERIALIZER")
        self._serializer: Serializer = (
            _import_serializer(serializer_path) if serializer_path else JsonSerializer()
        )
        self._service: Any = None

    # ---- infrastructure ---------------------------------------------------

    @property
    def _redis(self) -> Any:
        if self._service is None:
            self._service = build_redis_service(self._location)
        return self._service

    def _resolve_ttl(self, timeout: Any) -> int | None | Any:
        """Return ``None`` (persist), ``0`` (delete), or positive seconds.

        ``DEFAULT_TIMEOUT`` (the sentinel Django passes when the caller did
        not specify one) is replaced by ``self.default_timeout``.
        """
        if timeout is DEFAULT_TIMEOUT:
            timeout = self.default_timeout
        if timeout is None:
            return None
        try:
            ttl = int(timeout)
        except (TypeError, ValueError):
            return None
        if ttl <= 0:
            return 0
        return ttl

    def _dump(self, value: Any) -> str:
        return self._serializer.dumps(value)

    def _load(self, raw: str | None, default: Any) -> Any:
        if raw is None:
            return default
        return self._serializer.loads(raw)

    # ---- async core -------------------------------------------------------

    async def aget(self, key: Any, default: Any = None, version: Any = None) -> Any:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        raw = await self._redis.string.get(real_key)
        return self._load(raw, default)

    async def aset(
        self,
        key: Any,
        value: Any,
        timeout: Any = DEFAULT_TIMEOUT,
        version: Any = None,
    ) -> None:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        ttl = self._resolve_ttl(timeout)
        if ttl == 0:
            await self._redis.string.delete(real_key)
            return
        payload = self._dump(value)
        await self._redis.string.set(real_key, payload, ttl=ttl)

    async def aadd(
        self,
        key: Any,
        value: Any,
        timeout: Any = DEFAULT_TIMEOUT,
        version: Any = None,
    ) -> bool:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        ttl = self._resolve_ttl(timeout)
        if ttl == 0:
            return False
        payload = self._dump(value)
        return bool(await self._redis.string.setnx(real_key, payload, ttl=ttl))

    async def adelete(self, key: Any, version: Any = None) -> bool:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        existed = await self._redis.string.exists(real_key)
        if not existed:
            return False
        await self._redis.string.delete(real_key)
        return True

    async def ahas_key(self, key: Any, version: Any = None) -> bool:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        return bool(await self._redis.string.exists(real_key))

    async def atouch(
        self,
        key: Any,
        timeout: Any = DEFAULT_TIMEOUT,
        version: Any = None,
    ) -> bool:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        ttl = self._resolve_ttl(timeout)
        if ttl == 0:
            existed = await self._redis.string.exists(real_key)
            if existed:
                await self._redis.string.delete(real_key)
            return bool(existed)
        if ttl is None:
            # Persist: drop TTL via PERSIST — but redis-py exposes it through
            # the client. Use the raw client to avoid widening the platform API.
            return bool(await self._redis.string.client.persist(real_key))
        return bool(await self._redis.string.expire(real_key, ttl))

    async def aget_many(self, keys: Iterable[Any], version: Any = None) -> dict[Any, Any]:
        key_list = list(keys)
        if not key_list:
            return {}
        real_keys = [self.make_key(k, version=version) for k in key_list]
        for real in real_keys:
            self.validate_key(real)
        raws = await self._redis.string.mget(*real_keys)
        result: dict[Any, Any] = {}
        for original, raw in zip(key_list, raws, strict=True):
            if raw is None:
                continue
            result[original] = self._serializer.loads(raw)
        return result

    async def aset_many(
        self,
        mapping: dict[Any, Any],
        timeout: Any = DEFAULT_TIMEOUT,
        version: Any = None,
    ) -> list[Any]:
        if not mapping:
            return []
        for original in mapping:
            await self.aset(original, mapping[original], timeout=timeout, version=version)
        return []

    async def adelete_many(self, keys: Iterable[Any], version: Any = None) -> None:
        for key in keys:
            await self.adelete(key, version=version)

    async def aincr(self, key: Any, delta: int = 1, version: Any = None) -> int:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        if not await self._redis.string.exists(real_key):
            raise ValueError(f"Key '{key}' not found")
        return int(await self._redis.string.incrby(real_key, delta))

    async def adecr(self, key: Any, delta: int = 1, version: Any = None) -> int:
        return await self.aincr(key, -delta, version=version)

    async def aclear(self) -> None:
        if not self.key_prefix:
            raise ImproperlyConfigured(
                "codex_django RedisCache.clear() requires CACHES['default']['KEY_PREFIX'] "
                "to be set; refusing to run an unbounded SCAN+DEL."
            )
        await self._redis.string.delete_by_pattern(f"{self.key_prefix}:*")

    # ---- sync wrappers ----------------------------------------------------

    def get(self, key: Any, default: Any = None, version: Any = None) -> Any:
        return async_to_sync(self.aget)(key, default, version)

    def set(
        self,
        key: Any,
        value: Any,
        timeout: Any = DEFAULT_TIMEOUT,
        version: Any = None,
    ) -> None:
        async_to_sync(self.aset)(key, value, timeout, version)

    def add(
        self,
        key: Any,
        value: Any,
        timeout: Any = DEFAULT_TIMEOUT,
        version: Any = None,
    ) -> bool:
        return async_to_sync(self.aadd)(key, value, timeout, version)

    def delete(self, key: Any, version: Any = None) -> bool:
        return async_to_sync(self.adelete)(key, version)

    def has_key(self, key: Any, version: Any = None) -> bool:
        return async_to_sync(self.ahas_key)(key, version)

    def touch(
        self,
        key: Any,
        timeout: Any = DEFAULT_TIMEOUT,
        version: Any = None,
    ) -> bool:
        return async_to_sync(self.atouch)(key, timeout, version)

    def get_many(self, keys: Iterable[Any], version: Any = None) -> dict[Any, Any]:
        return async_to_sync(self.aget_many)(keys, version)

    def set_many(
        self,
        mapping: dict[Any, Any],
        timeout: Any = DEFAULT_TIMEOUT,
        version: Any = None,
    ) -> list[Any]:
        return async_to_sync(self.aset_many)(mapping, timeout, version)

    def delete_many(self, keys: Iterable[Any], version: Any = None) -> None:
        async_to_sync(self.adelete_many)(keys, version)

    def incr(self, key: Any, delta: int = 1, version: Any = None) -> int:
        return async_to_sync(self.aincr)(key, delta, version)

    def decr(self, key: Any, delta: int = 1, version: Any = None) -> int:
        return async_to_sync(self.adecr)(key, delta, version)

    def clear(self) -> None:
        async_to_sync(self.aclear)()
