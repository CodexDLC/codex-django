<!-- DOC_TYPE: GUIDE -->

# Redis Cache и Session

## Когда использовать

Используйте эти бэкенды, когда проекту нужен Redis-бэкенд для Django-сессий и
основного кэша без pickle и без зависимости `django-redis`. Стек строится
поверх `codex-platform` / `codex-django` и совместим с остальными Redis-менеджерами проекта.

## Минимальная настройка

```python
# settings.py (production / staging)
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
PROJECT_NAME = "myproject"

CACHES = {
    "default": {
        "BACKEND": "codex_django.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": PROJECT_NAME,   # обязательно — используется в clear()
        "TIMEOUT": 300,
    }
}

SESSION_ENGINE = "codex_django.sessions.backends.redis"
SESSION_COOKIE_NAME = f"sessionid_{PROJECT_NAME}"
SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"

RATELIMIT_USE_CACHE = "default"   # django-ratelimit работает без изменений
```

`SESSION_CACHE_ALIAS` больше не нужен — session backend подключается к Redis
напрямую, а не через cache framework.

## Справочник настроек

| Настройка | По умолчанию | Примечание |
|---|---|---|
| `CACHES["default"]["KEY_PREFIX"]` | `""` | Обязательно. Область видимости для `clear()`. |
| `CACHES["default"]["TIMEOUT"]` | `300` | TTL в секундах по умолчанию. |
| `CACHES["default"]["OPTIONS"]["SERIALIZER"]` | `JsonSerializer` | Dotted path к пользовательскому классу. |
| `CODEX_SESSION_REDIS_URL` | `settings.REDIS_URL` | Переопределяет URL Redis только для сессий. |
| `CODEX_SESSION_KEY_PREFIX` | `"session"` | Средний сегмент Redis-ключа сессии. |

Структура ключей:

```
{PROJECT_NAME}:{CODEX_SESSION_KEY_PREFIX}:{session_key}  # сессии
{KEY_PREFIX}:{VERSION}:{cache_key}                        # кэш
```

## Переопределения для dev и test

```python
# settings/dev.py
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# settings/test.py
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
```

## Политика no-pickle

Ни один из бэкендов не использует `pickle`:

- Сессии хранятся как Django **encoded string** — подписанная JSON-строка,
  сгенерированная `SessionBase.encode()`.
- Кэш хранит строгий JSON через `JsonSerializer`. Попытка сохранить значение,
  которое нельзя закодировать (`datetime`, `Decimal`, `set` и т. д.),
  вызывает `TypeError` немедленно.

Для нестандартных типов используйте `codex_django.cache.values.CacheCoder`:

```python
from codex_django.cache.values import CacheCoder
from django.core.cache import cache

cache.set("user:42:last_seen", CacheCoder.dump_datetime(user.last_seen), 3600)
raw = cache.get("user:42:last_seen")
last_seen = CacheCoder.load_datetime(raw) if raw else None
```

`CacheCoder` также поддерживает `date`, `timedelta`, `Decimal`, `UUID`, `set`,
`bytes` и рекурсивный `CacheCoder.dump()` для вложенных структур.

## clear() работает в пределах namespace

`cache.clear()` делает `SCAN + DEL` по маске `{KEY_PREFIX}:*`. Команда
`FLUSHDB` **никогда не выполняется**. Если `KEY_PREFIX` пуст, `clear()`
вызывает `ImproperlyConfigured` вместо очистки неограниченного пространства.

## Поведение при сбое Redis

Оба бэкенда пробрасывают `RedisConnectionError` и `RedisServiceError` без
перехвата — нет тихого fallback, нет пустой сессии при недоступности Redis,
нет обхода через `CODEX_REDIS_ENABLED`.

## Миграция с django-redis

1. Замените `BACKEND` на `"codex_django.cache.backends.redis.RedisCache"`.
2. Удалите `OPTIONS["CLIENT_CLASS"]`.
3. Замените `SESSION_ENGINE` на `"codex_django.sessions.backends.redis"`.
4. Удалите `SESSION_CACHE_ALIAS`.
5. Старые pickled-данные **не читаются** — сессии сбросятся при переключении.
6. После проверки удалите `django-redis` из зависимостей проекта.

## Точки входа

- `codex_django.sessions.backends.redis.SessionStore`
- `codex_django.cache.backends.redis.RedisCache`
- `codex_django.cache.serializers.JsonSerializer`
- `codex_django.cache.values.CacheCoder`

## Связанные разделы

- Архитектура: [Redis Cache и Session Layer](../architecture/redis.md)
