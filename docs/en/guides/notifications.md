<!-- DOC_TYPE: GUIDE -->

# Notifications Guide

## When To Use It

Do not use `notifications` for new code. It remains as a deprecated compatibility path for projects that have not yet migrated to `codex_django.messaging`.

Use [Messaging Guide](messaging.md) for new email content models, payload builders, delivery adapters, audience batching, and cabinet bridge contracts.

## Add The Scaffold

```bash
codex-django add-notifications --app system --project myproject
```

If your ARQ client should live outside the default location, pass `--arq-dir`.

## What Gets Added

- notification feature files under `features/<app_name>/`
- ARQ client scaffolding under `core/arq/` or your custom target

## Follow-Up Wiring

1. Register `EmailContent` in admin.
2. Run migrations.
3. Set `ARQ_REDIS_URL` in Django settings.
4. Extend `NotificationService` with your project-specific events.

## Runtime Entry Points

- Legacy: `codex_django.notifications`
- Canonical replacement: `codex_django.messaging`
- Canonical adapters: `codex_django.messaging.adapters`
- Canonical mixins: `codex_django.messaging.mixins`

Legacy package-level imports emit `DeprecationWarning`, but old imports remain usable during the deprecation window.

## Related Reading

- Architecture: `messaging`
- API reference: `codex_django.messaging`
- Compatibility API: `codex_django.notifications`
