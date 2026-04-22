# План реализации: Трек B (codex-django Redis Backends)

В соответствии с документом `redis-backends-recovery.md`, зависимость `codex-platform` уже обновлена до `>=0.4.0` в `pyproject.toml`.
Ниже представлен план по реализации Трека B (миграция `BaseDjangoRedisManager` и его потребителей).

## User Review Required

> [!IMPORTANT]
> Требуется ваше подтверждение (явное согласие) для начала выполнения этого плана. Изменения носят ломающий характер (breaking change), так как старые атрибуты (`self._client`, `self.string`, `self.hash`) будут полностью удалены, а `BaseDjangoRedisManager` перестанет наследоваться от `codex_platform.BaseRedisManager`.

## Open Questions

Нет блокирующих вопросов. Однако, перед началом написания кода, убедитесь, что:
- Вы согласны с тем, что мы полностью удаляем вызовы `async_to_sync` в кэше и сессиях.

## Proposed Changes

### core

#### [MODIFY] base.py (src/codex_django/core/redis/managers/base.py)
Переписать `BaseDjangoRedisManager` с нуля:
- Удалить наследование от `BaseRedisManager`.
- Добавить реализацию `async_client_factory` и `sync_client_factory`.
- Реализовать 4 контекстных менеджера: `@asynccontextmanager async def async_string()`, `@asynccontextmanager async def async_hash()`, `@contextmanager def sync_string()`, `@contextmanager def sync_hash()`.
- Удалить свойства `self.string`, `self.hash` и атрибут `self._client`.

### cache

#### [MODIFY] redis.py (src/codex_django/cache/backends/redis.py)
- Перевести все синхронные методы (`get`, `set`, `delete`, и т.д.) на использование `with self.sync_string() as s` или `with self.sync_hash() as h`.
- Перевести все асинхронные методы (`aget`, `aset`, и т.д.) на использование `async with self.async_string() as s`.
- Полностью удалить использование `async_to_sync` из синхронных путей выполнения.

### sessions

#### [MODIFY] redis.py (src/codex_django/sessions/backends/redis.py)
- Перевести синхронные методы (`save`, `load`, `exists`, `create`, `delete`) на `sync_string()`.
- Перевести асинхронные методы на `async_string()`.

### system

#### [MODIFY] fixtures.py (src/codex_django/system/redis/managers/fixtures.py)
- Мигрировать логику работы с Redis на использование новых контрактов (`sync_string()` / `async_string()`).

### tests

#### [NEW] test_base_manager_client_factory.py (tests/unit/core/redis/test_base_manager_client_factory.py)
- Тесты на injection фабрик, дефолтные фабрики, а также вызовы `close()` и `aclose()`.

#### [MODIFY] test_redis_backend_sync.py (tests/unit/sessions/test_redis_backend_sync.py)
- Обновить тесты синхронных путей сессий под новый API менеджера.

#### [MODIFY] test_redis_backend_sync.py (tests/unit/cache/test_redis_backend_sync.py)
- Обновить тесты синхронных путей кэша под новый API менеджера.

## Verification Plan

### Automated Tests
Будут запущены следующие команды для проверки покрытия и корректности работы:
- `pytest tests/unit/core/redis/test_base_manager_client_factory.py`
- `pytest tests/unit/sessions/test_redis_backend_sync.py`
- `pytest tests/unit/cache/test_redis_backend_sync.py`
- Обязательный Grep-gate: поиск `self._client`, `.string.` и `.hash.` для проверки отсутствия немигрированного кода.

### Manual Verification
После выполнения этого этапа потребуется запустить полную проверку проекта через `pytest`, чтобы убедиться, что ни один другой модуль в `codex-django` не сломался от изменения публичного API `BaseDjangoRedisManager`.
