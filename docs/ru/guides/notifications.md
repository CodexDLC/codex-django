<!-- DOC_TYPE: GUIDE -->

# Notifications Guide

## Когда использовать

Используйте `notifications`, когда проекту нужны email content models, builders для payload, delivery adapters и при необходимости ARQ-backed background dispatch.

## Добавление scaffold

```bash
codex-django add-notifications --app system --project myproject
```

Если ARQ client должен лежать не в стандартном месте, передайте `--arq-dir`.

## Что будет создано

- notification feature files в `features/<app_name>/`
- ARQ client scaffold в `core/arq/` или в вашем custom target

## Что нужно подключить после генерации

1. Зарегистрировать `EmailContent` в admin.
2. Выполнить миграции.
3. Указать `ARQ_REDIS_URL` в Django settings.
4. Расширить `NotificationService` своими project-specific events.

## Основные точки входа

- `codex_django.notifications`
- `codex_django.notifications.adapters`
- `codex_django.notifications.mixins`

## Связанные разделы

- Architecture: `notifications`
- API reference: `codex_django.notifications`
