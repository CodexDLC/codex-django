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
from typing import Any, cast

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT, BaseCache
from django.core.exceptions import ImproperlyConfigured
from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis

from codex_django.cache.serializers import JsonSerializer, Serializer
from codex_django.core.redis.managers.base import BaseDjangoRedisManager

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
        self._location = str(server or getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))
        options = params.get("OPTIONS") or {}
        serializer_path = options.get("SERIALIZER")
        self._serializer: Serializer = _import_serializer(serializer_path) if serializer_path else JsonSerializer()
        self._manager: BaseDjangoRedisManager | None = None

    # ---- infrastructure ---------------------------------------------------

    @property
    def redis_manager(self) -> BaseDjangoRedisManager:
        if self._manager is None:

            def async_factory() -> AsyncRedis:
                return cast(AsyncRedis, AsyncRedis.from_url(self._location, decode_responses=True))

            def sync_factory() -> SyncRedis:
                return SyncRedis.from_url(self._location, decode_responses=True)

            self._manager = BaseDjangoRedisManager(
                prefix=self.key_prefix,
                async_client_factory=async_factory,
                sync_client_factory=sync_factory,
            )
        return self._manager

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
        async with self.redis_manager.async_string() as s:
            raw = await s.get(real_key)
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
            async with self.redis_manager.async_string() as s:
                await s.delete(real_key)
            return
        payload = self._dump(value)
        async with self.redis_manager.async_string() as s:
            await s.set(real_key, payload, ttl=ttl)

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
        async with self.redis_manager.async_string() as s:
            # Use raw client for setnx + ex since operations wrapper might not support atomic setnx with ex
            # Actually StringOperations set_nx doesn't take ttl in some versions, or maybe it uses set(nx=True)
            # We'll use the raw client exposed by operation or directly if not available.
            return bool(await s.client.set(real_key, payload, nx=True, ex=ttl))

    async def adelete(self, key: Any, version: Any = None) -> bool:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        async with self.redis_manager.async_string() as s:
            existed = await s.exists(real_key)
            if not existed:
                return False
            await s.delete(real_key)
        return True

    async def ahas_key(self, key: Any, version: Any = None) -> bool:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        async with self.redis_manager.async_string() as s:
            return bool(await s.exists(real_key))

    async def atouch(
        self,
        key: Any,
        timeout: Any = DEFAULT_TIMEOUT,
        version: Any = None,
    ) -> bool:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        ttl = self._resolve_ttl(timeout)
        async with self.redis_manager.async_string() as s:
            if ttl == 0:
                existed = await s.exists(real_key)
                if existed:
                    await s.delete(real_key)
                return bool(existed)
            if ttl is None:
                return bool(await s.client.persist(real_key))
            return bool(await s.expire(real_key, ttl))

    async def aget_many(self, keys: Iterable[Any], version: Any = None) -> dict[Any, Any]:
        key_list = list(keys)
        if not key_list:
            return {}
        real_keys = [self.make_key(k, version=version) for k in key_list]
        for real in real_keys:
            self.validate_key(real)
        async with self.redis_manager.async_string() as s:
            raws = await s.mget(*real_keys)
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
        async with self.redis_manager.async_string() as s:
            if not await s.exists(real_key):
                raise ValueError(f"Key '{key}' not found")
            return int(await s.incr(real_key, delta))

    async def adecr(self, key: Any, delta: int = 1, version: Any = None) -> int:
        return await self.aincr(key, -delta, version=version)

    async def aclear(self) -> None:
        if not self.key_prefix:
            raise ImproperlyConfigured(
                "codex_django RedisCache.clear() requires CACHES['default']['KEY_PREFIX'] "
                "to be set; refusing to run an unbounded SCAN+DEL."
            )
        async with self.redis_manager.async_string() as s:
            # We'll collect and delete manually or use raw client's eval if needed,
            # but usually async clients have scan_iter
            cursor = 0
            pattern = f"{self.key_prefix}:*"
            while True:
                cursor, keys = await s.client.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    await s.client.delete(*keys)
                if cursor == 0:
                    break

    # ---- sync wrappers ----------------------------------------------------

    def get(self, key: Any, default: Any = None, version: Any = None) -> Any:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        with self.redis_manager.sync_string() as s:
            raw = s.get(real_key)
        return self._load(raw, default)

    def set(
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
            with self.redis_manager.sync_string() as s:
                s.delete(real_key)
            return
        payload = self._dump(value)
        with self.redis_manager.sync_string() as s:
            s.set(real_key, payload, ttl=ttl)

    def add(
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
        with self.redis_manager.sync_string() as s:
            return bool(s.client.set(real_key, payload, nx=True, ex=ttl))

    def delete(self, key: Any, version: Any = None) -> bool:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        with self.redis_manager.sync_string() as s:
            existed = s.exists(real_key)
            if not existed:
                return False
            s.delete(real_key)
        return True

    def has_key(self, key: Any, version: Any = None) -> bool:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        with self.redis_manager.sync_string() as s:
            return bool(s.exists(real_key))

    def touch(
        self,
        key: Any,
        timeout: Any = DEFAULT_TIMEOUT,
        version: Any = None,
    ) -> bool:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        ttl = self._resolve_ttl(timeout)
        with self.redis_manager.sync_string() as s:
            if ttl == 0:
                existed = s.exists(real_key)
                if existed:
                    s.delete(real_key)
                return bool(existed)
            if ttl is None:
                return bool(s.client.persist(real_key))
            return bool(s.expire(real_key, ttl))

    def get_many(self, keys: Iterable[Any], version: Any = None) -> dict[Any, Any]:
        key_list = list(keys)
        if not key_list:
            return {}
        real_keys = [self.make_key(k, version=version) for k in key_list]
        for real in real_keys:
            self.validate_key(real)
        with self.redis_manager.sync_string() as s:
            raws = s.mget(*real_keys)
        result: dict[Any, Any] = {}
        for original, raw in zip(key_list, raws, strict=True):
            if raw is None:
                continue
            result[original] = self._serializer.loads(raw)
        return result

    def set_many(
        self,
        mapping: dict[Any, Any],
        timeout: Any = DEFAULT_TIMEOUT,
        version: Any = None,
    ) -> list[Any]:
        if not mapping:
            return []
        for original in mapping:
            self.set(original, mapping[original], timeout=timeout, version=version)
        return []

    def delete_many(self, keys: Iterable[Any], version: Any = None) -> None:
        for key in keys:
            self.delete(key, version=version)

    def incr(self, key: Any, delta: int = 1, version: Any = None) -> int:
        real_key = self.make_key(key, version=version)
        self.validate_key(real_key)
        with self.redis_manager.sync_string() as s:
            if not s.exists(real_key):
                raise ValueError(f"Key '{key}' not found")
            return int(s.incr(real_key, delta))

    def decr(self, key: Any, delta: int = 1, version: Any = None) -> int:
        return self.incr(key, -delta, version=version)

    def clear(self) -> None:
        if not self.key_prefix:
            raise ImproperlyConfigured(
                "codex_django RedisCache.clear() requires CACHES['default']['KEY_PREFIX'] "
                "to be set; refusing to run an unbounded SCAN+DEL."
            )
        with self.redis_manager.sync_string() as s:
            client: Any = s.client
            cursor = 0
            pattern = f"{self.key_prefix}:*"
            while True:
                cursor, keys = client.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    client.delete(*keys)
                if cursor == 0:
                    break
