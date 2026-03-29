<!-- DOC_TYPE: GUIDE -->

# Cabinet Guide

## When To Use It

Use `cabinet` when you need a reusable client-facing dashboard layer with navigation widgets, cached cabinet settings, and profile-oriented pages.

## Add The Scaffold

```bash
codex-django add-client-cabinet --project myproject
```

## What Gets Added

- cabinet adapters and client views
- cabinet client templates
- `UserProfile` model under `system/models/`

## Follow-Up Wiring

1. Enable the generated cabinet adapter settings in the scaffolded settings module.
2. Add the generated client cabinet URL patterns to `cabinet/urls.py`.
3. Export `UserProfile` from `system/models/__init__.py`.
4. Run migrations.

## Runtime Entry Points

- `codex_django.cabinet`
- `codex_django.cabinet.selector`
- `codex_django.cabinet.redis`

## Related Reading

- Architecture: `cabinet`
- API reference: `codex_django.cabinet`
