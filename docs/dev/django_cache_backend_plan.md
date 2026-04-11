# Django Cache Backend Plan

This document tracks a future library task for `codex-django`: provide a
native Django cache/session backend on top of the existing
`codex-platform` / `codex-django` Redis layer.

This is explicitly a future engineering task. It is not a blocker for the
current `Django 6.0.4+` upgrade path as long as `django-redis` remains usable
for cache/session wiring during that transition.

## 1. Goal

Add a reusable Django cache backend for `codex-django` projects that:

- uses the internal Redis stack instead of `django-redis`
- supports `CACHES["default"]`
- can back `django.contrib.sessions.backends.cache`
- aligns cache/session behavior with the existing codex Redis abstractions
- avoids `pickle` as the default serialization strategy

## 2. Why this exists

Today, `codex-django` already has a Redis-oriented runtime layer for Django
integrations, but standard Django cache/session usage may still depend on
`django-redis`.

That leaves an architectural split:

- runtime managers use `codex-platform` / `codex-django` Redis abstractions
- Django cache/session may still use a separate adapter

The target direction is one Redis stack for both runtime features and Django
cache/session integration.

## 3. Available foundation

The required Redis primitives already exist in the platform layer, including:

- base Redis managers
- string/hash operations
- pipeline helpers
- TTL and related expiration primitives

The Django-aware Redis layer also already exists in `codex-django`, so this is
not a from-scratch Redis implementation task. The missing piece is the Django
cache backend adapter layer.

## 4. Required backend surface

The first implementation should cover the practical Django cache contract:

- `get()`
- `set()`
- `add()`
- `delete()`
- `get_many()`
- `set_many()`
- `delete_many()`
- `clear()`
- `touch()`
- key prefix / version handling
- timeout semantics compatible with Django expectations

Session compatibility should then be validated explicitly on top of that.

## 5. Serialization policy

The backend should define an explicit serialization strategy for:

- strings
- JSON-serializable payloads
- non-JSON-compatible values

Preferred direction:

- JSON-first where possible
- explicit serializer selection for unsupported payloads
- no silent `pickle` default

If `pickle` support exists at all, it should be explicit opt-in rather than the
default behavior.

## 6. Open design questions

Questions to resolve during implementation:

- exact backend module location in `codex-django`
- whether any extra Redis primitives must be promoted into `codex-platform`
- namespace/version handling for cache keys
- `clear()` semantics

Expected direction for `clear()`:

- namespace-scoped clear
- no broad Redis flush as default behavior

## 7. Sequencing

Suggested order:

1. Confirm the current Django 6 upgrade can proceed without replacing
   `django-redis`.
2. Design the `codex-django` backend API and serializer policy.
3. Implement the minimal backend contract.
4. Validate Django cache operations and session behavior.
5. Document migration from `django-redis` and update project templates later.

## 8. Status

Status: planned

Priority: post-Django-6 upgrade task

Trigger to start:

- current upgrade path is stabilized
- immediate runtime blockers are resolved
