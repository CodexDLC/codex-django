<!-- DOC_TYPE: GUIDE -->

# Booking Guide

## When To Use It

Use `booking` when your Django project needs ORM-backed scheduling, slot discovery, booking creation, and optional multi-service chains on top of the `codex-services` engine.

## Add The Scaffold

```bash
codex-django add-booking --project myproject
```

## What Gets Added

- `booking/` application files
- booking settings files under `system/`
- cabinet booking views and templates
- booking page templates and partials

## Follow-Up Wiring

After scaffolding, wire the generated code into your project:

1. Add `booking` to `INSTALLED_APPS` or `LOCAL_APPS`.
2. Export `BookingSettings` from `system/models/__init__.py`.
3. Register the generated admin integration for booking settings.
4. Run migrations for `booking` and `system`.
5. Include `booking.urls` in the project URL configuration.
6. Expose the generated cabinet booking URLs if you use cabinet pages.

## Runtime Entry Points

- `codex_django.booking`
- `codex_django.booking.selectors`
- `codex_django.booking.adapters`
- `codex_django.booking.mixins`

## Related Reading

- Architecture: `booking`
- API reference: `codex_django.booking`
