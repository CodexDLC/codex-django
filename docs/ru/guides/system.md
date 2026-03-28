<!-- DOC_TYPE: GUIDE -->

# System Guide

## Когда использовать

Используйте `system`, когда проекту нужны центральные project-state models: site settings, fixture orchestration, admin-facing runtime configuration и shared integrations.

## Типичные зоны ответственности

- site settings и static content
- состояние внешних интеграций во время работы проекта
- fixture hash и helpers для orchestration
- переиспользуемые system mixins для project models

## Как это связано с другими модулями

`system` это административный backbone для остальных частей:

1. `booking` хранит booking defaults через booking settings.
2. `cabinet` расширяет project-level user profile и dashboard settings.
3. `notifications` часто размещает content models и orchestration hooks рядом с system-данными.

## Основные точки входа

- `codex_django.system`
- `codex_django.system.mixins`
- `codex_django.system.redis`
- `codex_django.system.management`

## Связанные разделы

- Architecture: `system`
- API reference: `codex_django.system`
