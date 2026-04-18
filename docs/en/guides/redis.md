<!-- DOC_TYPE: GUIDE -->

# Redis Cache and Session Guide

## When To Use It

Use these backends when your project needs a no-pickle, JSON-only Redis store for
Django sessions and the default cache, and you want to stay on the
`codex-platform` / `codex-django` Redis stack without adding `django-redis` as a
separate dependency.

## Minimal Settings Wiring

```python
# settings.py (production / staging)
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
PROJECT_NAME = "myproject"

CACHES = {
    "default": {
        "BACKEND": "codex_django.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": PROJECT_NAME,   # required — see "clear()" below
        "TIMEOUT": 300,
    }
}

SESSION_ENGINE = "codex_django.sessions.backends.redis"
SESSION_COOKIE_NAME = f"sessionid_{PROJECT_NAME}"
SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"

RATELIMIT_USE_CACHE = "default"   # django-ratelimit works unchanged
```

There is no `SESSION_CACHE_ALIAS` — the session backend connects to Redis
directly.

## Settings Reference

| Setting | Default | Notes |
|---|---|---|
| `CACHES["default"]["KEY_PREFIX"]` | `""` | Required. Scopes `clear()`. |
| `CACHES["default"]["TIMEOUT"]` | `300` | Default TTL in seconds. |
| `CACHES["default"]["OPTIONS"]["SERIALIZER"]` | `JsonSerializer` | Dotted path to a custom class. |
| `CODEX_SESSION_REDIS_URL` | `settings.REDIS_URL` | Override Redis URL for sessions only. |
| `CODEX_SESSION_KEY_PREFIX` | `"session"` | Middle segment of the Redis key. |

Redis keys created by this layer follow the same convention as other
`codex-django` managers:

```
{PROJECT_NAME}:{CODEX_SESSION_KEY_PREFIX}:{session_key}  # sessions
{KEY_PREFIX}:{VERSION}:{cache_key}                        # cache
```

## Dev and Test Overrides

These backends talk to a live Redis; keep dev / test overrides in place:

```python
# settings/dev.py
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# settings/test.py
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
```

## No-Pickle Contract

Neither backend uses `pickle`:

- Sessions store the Django **encoded string** — a signed, JSON-serialized
  blob produced by `SessionBase.encode()`.
- Cache stores strict JSON via `JsonSerializer`. Setting a value that cannot
  be encoded (`datetime`, `Decimal`, `set`, …) raises `TypeError` immediately.

To cache non-JSON-native types, use the helpers in
`codex_django.cache.values.CacheCoder`:

```python
from codex_django.cache.values import CacheCoder
from django.core.cache import cache

# Store
cache.set("user:42:last_seen", CacheCoder.dump_datetime(user.last_seen), 3600)

# Retrieve
raw = cache.get("user:42:last_seen")
last_seen = CacheCoder.load_datetime(raw) if raw else None
```

`CacheCoder` also has helpers for `date`, `timedelta`, `Decimal`, `UUID`,
`set`, and `bytes`, plus a recursive `CacheCoder.dump()` for nested structures.

## clear() Is Namespace-Scoped

`cache.clear()` does a `SCAN + DEL` for `{KEY_PREFIX}:*`. It **never** calls
`FLUSHDB`. If `KEY_PREFIX` is empty, `clear()` raises `ImproperlyConfigured`
rather than wiping unscoped data.

## Redis Failure Policy

Both backends propagate `RedisConnectionError` and `RedisServiceError` to the
caller. There is no silent fallback, no empty-session return on outage, and no
`CODEX_REDIS_ENABLED` bypass — session and cache behavior must be deterministic
in every environment.

## Migrating from django-redis

If your project currently uses `django_redis.cache.RedisCache`:

1. Replace `BACKEND` with `"codex_django.cache.backends.redis.RedisCache"`.
2. Remove `OPTIONS["CLIENT_CLASS"]` (not applicable).
3. Replace `SESSION_ENGINE` with `"codex_django.sessions.backends.redis"`.
4. Remove `SESSION_CACHE_ALIAS`.
5. Old pickled entries are **not** read — sessions become invalid at cut-over
   (users re-authenticate), cached entries expire on their TTL.
6. After smoke-testing, remove `django-redis` from your project dependencies.

## Runtime Entry Points

- `codex_django.sessions.backends.redis.SessionStore`
- `codex_django.cache.backends.redis.RedisCache`
- `codex_django.cache.serializers.JsonSerializer`
- `codex_django.cache.values.CacheCoder`

## Related Reading

- Architecture: [Redis Cache and Session Layer](../architecture/redis.md)
- API Reference: [Redis cache and session internals](../api/internal/redis.md)
