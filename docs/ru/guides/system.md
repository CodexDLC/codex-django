<!-- DOC_TYPE: GUIDE -->

# System Guide

## Когда использовать

Используйте `system`, когда проекту нужны центральные project-state models: site settings, fixture orchestration, admin-facing runtime configuration и shared integrations.

## Типичные зоны ответственности

- site settings и static content
- состояние внешних интеграций во время работы проекта
- fixture hash и helpers для orchestration
- базовые команды для JSON fixture upsert и singleton update
- временные Redis action tokens для confirmation-flow
- переиспользуемые system mixins для project models

## Команды загрузки фикстур

Используйте `JsonFixtureUpsertCommand` для Django-style JSON фикстур, где файл содержит список объектов с `fields`. Проектная команда задает путь к фикстуре, модель, fixture hash key и lookup field; библиотека берет на себя JSON loading, validation, `update_or_create`, counters и сохранение hash.

Используйте `SingletonFixtureUpdateCommand` для singleton-состояния проекта вроде `SiteSettings`. Команда читает первую строку фикстуры, обновляет только изменившиеся поля модели, сохраняет только при изменениях и синхронизирует instance через Redis manager site settings.

`BaseUpdateAllContentCommand` по-прежнему запускает список `commands_to_run`, но теперь имеет optional hooks для вывода секций вокруг subcommands и сохраняет forwarding `--force`.

## Action Tokens

`JsonActionTokenRedisManager` хранит временные JSON payloads за secure URL-safe tokens. Проект оставляет у себя форму payload и URL logic, а библиотека отвечает за token generation, Redis keying, TTL, JSON decode и delete behavior.

## Как это связано с другими модулями

`system` это административный backbone для остальных частей:

1. `booking` хранит booking defaults через booking settings.
2. `cabinet` расширяет project-level user profile и dashboard settings.
3. `notifications` часто размещает content models и orchestration hooks рядом с system-данными.

## Основные точки входа

- `codex_django.system`
- `codex_django.system.mixins`
- `codex_django.system.redis`
- `codex_django.system.redis.managers.JsonActionTokenRedisManager`
- `codex_django.system.management`
- `codex_django.system.management.JsonFixtureUpsertCommand`
- `codex_django.system.management.SingletonFixtureUpdateCommand`

## Связанные разделы

- Architecture: `system`
- API reference: `codex_django.system`
