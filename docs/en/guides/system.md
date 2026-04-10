<!-- DOC_TYPE: GUIDE -->

# System Guide

## When To Use It

Use `system` when your project needs central project-state models such as site settings, fixture orchestration, admin-facing runtime configuration, and shared integrations.

## Typical Responsibilities

- site settings and static content
- runtime integration state
- fixture hash and fixture orchestration helpers
- reusable JSON fixture upsert and singleton update command bases
- temporary Redis-backed action tokens for confirmation flows
- reusable system mixins for project models

## Fixture Import Commands

Use `JsonFixtureUpsertCommand` for Django-style JSON fixture files that contain a list of objects with a `fields` mapping. Configure the fixture path, target model, fixture hash key, and lookup field in the project command; the library handles JSON loading, validation, `update_or_create`, counters, and hash persistence.

Use `SingletonFixtureUpdateCommand` for one-row project state such as `SiteSettings`. It loads the first fixture row, updates only changed model fields, saves only when needed, and synchronizes the instance through the site settings Redis manager.

`BaseUpdateAllContentCommand` still runs a configured `commands_to_run` list and now exposes optional hooks for section output around each subcommand while preserving `--force` forwarding.

## Action Tokens

`JsonActionTokenRedisManager` stores temporary JSON payloads behind secure URL-safe tokens. Projects keep their own payload shape and URLs, while the library owns token generation, Redis keying, TTL, JSON decoding, and delete behavior.

## Integration Notes

`system` is the administrative backbone for other modules:

1. `booking` stores booking defaults through booking settings.
2. `cabinet` extends project-level user profile and dashboard settings.
3. `notifications` often places content models or orchestration hooks alongside system data.

## Runtime Entry Points

- `codex_django.system`
- `codex_django.system.mixins`
- `codex_django.system.redis`
- `codex_django.system.redis.managers.JsonActionTokenRedisManager`
- `codex_django.system.management`
- `codex_django.system.management.JsonFixtureUpsertCommand`
- `codex_django.system.management.SingletonFixtureUpdateCommand`

## Related Reading

- Architecture: `system`
- API reference: `codex_django.system`
