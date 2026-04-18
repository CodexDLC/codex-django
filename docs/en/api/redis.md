<!-- DOC_TYPE: API -->

# Redis Cache and Session API

## Session backend

Set `SESSION_ENGINE = "codex_django.sessions.backends.redis"` in your
settings to activate the backend.

```python
from codex_django.sessions.backends.redis import SessionStore
```

`SessionStore` is a `SessionBase` subclass. All standard Django session
middleware and shortcuts work unchanged. The async-native methods
(`aexists`, `acreate`, `aload`, `asave`, `adelete`) are available for
ASGI views without wrapping.

## Cache backend

Set `CACHES["default"]["BACKEND"] = "codex_django.cache.backends.redis.RedisCache"`.

```python
from django.core.cache import cache

cache.set("key", {"data": 1}, timeout=300)
result = cache.get("key")   # {"data": 1}
```

## CacheCoder

```python
from codex_django.cache.values import CacheCoder

# datetime
raw = CacheCoder.dump_datetime(my_dt)
my_dt = CacheCoder.load_datetime(raw)

# Decimal
raw = CacheCoder.dump_decimal(my_decimal)
my_decimal = CacheCoder.load_decimal(raw)

# Recursive nested structure
payload = CacheCoder.dump({"at": my_dt, "price": my_decimal, "tags": {1, 2}})
cache.set("order:42", payload, 600)
```

## Custom serializer

```python
# myproject/cache.py
import orjson

class OrjsonSerializer:
    def dumps(self, value):
        return orjson.dumps(value).decode()
    def loads(self, raw):
        return orjson.loads(raw)
```

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "codex_django.cache.backends.redis.RedisCache",
        ...
        "OPTIONS": {"SERIALIZER": "myproject.cache.OrjsonSerializer"},
    }
}
```

For the generated module documentation, open
[Redis internals](internal/redis.md).
