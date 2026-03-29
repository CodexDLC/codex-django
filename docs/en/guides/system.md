<!-- DOC_TYPE: GUIDE -->

# System Guide

## When To Use It

Use `system` when your project needs central project-state models such as site settings, fixture orchestration, admin-facing runtime configuration, and shared integrations.

## Typical Responsibilities

- site settings and static content
- runtime integration state
- fixture hash and fixture orchestration helpers
- reusable system mixins for project models

## Integration Notes

`system` is the administrative backbone for other modules:

1. `booking` stores booking defaults through booking settings.
2. `cabinet` extends project-level user profile and dashboard settings.
3. `notifications` often places content models or orchestration hooks alongside system data.

## Runtime Entry Points

- `codex_django.system`
- `codex_django.system.mixins`
- `codex_django.system.redis`
- `codex_django.system.management`

## Related Reading

- Architecture: `system`
- API reference: `codex_django.system`
