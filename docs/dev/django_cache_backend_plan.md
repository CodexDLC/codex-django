# Django Cache and Session Backends

Status: **implemented** in codex-django 0.5.0. This document describes the
Redis-backed cache and session backends shipped with codex-django and the
migration path from `django-redis`.

## 1. What's included

Two independent, Redis-backed Django backends:

- `codex_django.sessions.backends.redis.SessionStore` — session engine.
- `codex_django.cache.backends.redis.RedisCache` — full Django cache backend.

Both sit on top of the existing `codex_platform.redis_service` async stack and
reuse `codex_django.core.redis.django_adapter` for client construction and
namespacing. Neither depends on `django-redis`.

## 2. No-pickle policy

Neither backend uses `pickle`:

- Session payload is stored as the Django **encoded string** produced by
  `SessionBase.encode()` — this requires `SESSION_SERIALIZER` to be a
  JSON-based serializer. Django's built-in
  `django.contrib.sessions.serializers.JSONSerializer` is the recommended
  choice (and is the default in modern Django).
- Cache values are stored as strict JSON via
  `codex_django.cache.serializers.JsonSerializer`. Values that cannot be
  JSON-encoded raise `TypeError` — there is **no** silent pickle fallback.

Old pickled keys left behind by `django-redis` are **not** readable and are
not migrated. The explicit expectation is that legacy sessions / cache entries
are dropped at cut-over (users simply re-authenticate).

## 3. Settings example

```python
# settings.py

REDIS_URL = "redis://localhost:6379/0"
PROJECT_NAME = "myproject"

CACHES = {
    "default": {
        "BACKEND": "codex_django.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,           # optional; defaults to settings.REDIS_URL
        "KEY_PREFIX": PROJECT_NAME,       # REQUIRED for clear() — see §6
        "TIMEOUT": 300,
        "OPTIONS": {
            # Optional: dotted path to a custom serializer class.
            # "SERIALIZER": "myproject.cache.MySerializer",
        },
    }
}

SESSION_ENGINE = "codex_django.sessions.backends.redis"
SESSION_COOKIE_NAME = f"sessionid_{PROJECT_NAME}"
SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"

# Optional: override the middle segment of the session key namespace.
# Default is "session" → Redis key "{PROJECT_NAME}:session:{session_key}".
# CODEX_SESSION_KEY_PREFIX = "sess"

# django-ratelimit remains pointed at the default cache — no change required.
RATELIMIT_USE_CACHE = "default"
```

There is **no** `SESSION_CACHE_ALIAS` — the session backend talks to Redis
directly, not through the cache framework.

## 4. Serialization of complex types

The cache serializer is strict by design. Writing `datetime`, `date`,
`timedelta`, `Decimal`, `UUID`, `set`, or `bytes` to the cache raises
`TypeError`. To round-trip such values, use the explicit helpers in
`codex_django.cache.values.CacheCoder`:

```python
from codex_django.cache.values import CacheCoder
from django.core.cache import cache

cache.set("user:42:last_seen", CacheCoder.dump_datetime(user.last_seen), 3600)
raw = cache.get("user:42:last_seen")
last_seen = CacheCoder.load_datetime(raw) if raw else None
```

`CacheCoder.dump()` also accepts nested structures (`dict` / `list` /
`tuple`) and recursively converts known types to JSON-native forms. For the
reverse, the caller must know which field is which — JSON does not preserve
Python types, and codex-django intentionally does **not** smuggle magic type
tags into the serialized payload (that would leak into every Redis consumer
and make a future revert impossible).

If the default is not enough, plug a custom serializer via
`OPTIONS["SERIALIZER"]`. The class must expose `dumps(value) -> str` and
`loads(raw) -> Any`.

## 5. Failure semantics

Both backends treat Redis as a hard dependency:

- Session: Redis outage raises `RedisConnectionError` out of
  `save` / `load` / `exists` / `create` / `delete`. A broken Redis must
  never look like "empty session" — that would silently log users out and
  allow replay of cleared cookies.
- Cache: all operations propagate `RedisConnectionError` /
  `RedisServiceError`. No transparent fallback to an in-memory cache.

The `CODEX_REDIS_ENABLED=False` DEBUG bypass used by domain managers
(`SeoRedisManager`, etc.) does **not** apply here — session and cache behavior
must be deterministic regardless of the environment.

## 6. `clear()` is namespace-scoped

`cache.clear()` performs a `SCAN` + `DEL` scoped to `{KEY_PREFIX}:*`. If
`KEY_PREFIX` is empty, `clear()` refuses to run (raises
`ImproperlyConfigured`) — codex-django will **never** issue `FLUSHDB` against
a shared Redis.

Set `KEY_PREFIX = PROJECT_NAME` (or any non-empty value) to enable clear.

## 7. Migration from django-redis

For a project currently using `django_redis.cache.RedisCache` +
`django.contrib.sessions.backends.cache`:

1. Update `CACHES["default"]["BACKEND"]` to
   `codex_django.cache.backends.redis.RedisCache`.
2. Remove the `OPTIONS["CLIENT_CLASS"]` entry (no longer applicable).
3. Change `SESSION_ENGINE` to `codex_django.sessions.backends.redis`.
4. Remove `SESSION_CACHE_ALIAS` — the session backend does not use the cache
   framework.
5. Confirm `SESSION_SERIALIZER` is a JSON serializer.
6. Deploy; legacy sessions and cache entries expire or are orphaned — that is
   acceptable by design.
7. After the new stack is stable, remove `django-redis` from the project's
   dependencies.

`django-ratelimit` continues to work unchanged — it uses
`cache.add` + `cache.incr`, both of which are supported by `RedisCache`.

## 8. Design notes

- The session and cache backends do **not** inherit from
  `BaseDjangoRedisManager`. They build their own `RedisService` through
  `codex_django.core.redis.django_adapter.build_redis_service()` so that the
  local-dev `_is_disabled()` bypass of the domain managers cannot accidentally
  disable them.
- Both backends define async-native primitives (`aget`, `aset`, `aadd`,
  `aload`, `asave`, `acreate`, …) and synchronous wrappers via
  `asgiref.sync.async_to_sync`, matching the existing pattern used by domain
  managers such as `SeoRedisManager`.
- `RedisCache.add()` is atomic via Redis `SET NX EX`.
- Session `save(must_create=True)` uses the same `SET NX EX` primitive, so
  two simultaneous logins on the same fresh session key cannot both succeed.
