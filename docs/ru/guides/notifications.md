<!-- DOC_TYPE: GUIDE -->

# Notifications Guide

## Когда использовать

Не используйте `notifications` для нового кода. Этот пакет остался deprecated compatibility path для проектов, которые еще не перешли на `codex_django.messaging`.

Для новых email content models, payload builders, delivery adapters, audience batching и cabinet bridge contracts используйте [Messaging Guide](messaging.md).

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

- Legacy: `codex_django.notifications`
- Canonical replacement: `codex_django.messaging`
- Canonical adapters: `codex_django.messaging.adapters`
- Canonical mixins: `codex_django.messaging.mixins`

Package-level legacy imports выбрасывают `DeprecationWarning`, но старые import paths остаются рабочими на время deprecation window.

## Связанные разделы

- Architecture: `messaging`
- API reference: `codex_django.messaging`
- Compatibility API: `codex_django.notifications`
