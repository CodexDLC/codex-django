<!-- DOC_TYPE: GUIDE -->

# Notifications Guide

## When To Use It

Use `notifications` when your project needs email content models, message payload builders, delivery adapters, and optional ARQ-backed background dispatch.

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

- `codex_django.notifications`
- `codex_django.notifications.adapters`
- `codex_django.notifications.mixins`

## Related Reading

- Architecture: `notifications`
- API reference: `codex_django.notifications`
