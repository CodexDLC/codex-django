# System Domain Refactor Plan

Comparison scope:

- Library: `C:\install\projects\codex_tools\codex-django\src\codex_django\system`
- Project: `C:\install\projects\clients\lily_website\src\lily_backend\system`

This document is the System domain audit and staged plan. It does not apply
project-side Python changes. Lily changes listed here are cleanup notes for a
later synchronized project pass.

## 1. Findings

### Fixture import commands duplicate generic JSON upsert logic

Lily uses `BaseHashProtectedCommand`, but each content command repeats the same
flow: resolve one fixture path, open JSON, validate list shape, iterate items,
extract `fields`, select a lookup key, and call `update_or_create`.

Concrete project duplication:

- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_static_translations.py:20`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_static_translations.py:23`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_static_translations.py:55`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_seo.py:20`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_seo.py:23`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_seo.py:55`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_email_content.py:20`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_email_content.py:23`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_email_content.py:55`

Library support today stops at hash protection:

- `C:\install\projects\codex_tools\codex-django\src\codex_django\system\management\base_commands.py:78`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\system\management\base_commands.py:96`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\system\management\base_commands.py:105`

### Aggregate update command bypasses the library base behavior

Lily declares `commands_to_run`, but overrides `handle()` and calls subcommands
manually without forwarding `--force`. That bypasses the behavior already
provided by `BaseUpdateAllContentCommand`.

- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_all_content.py:15`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_all_content.py:22`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_all_content.py:25`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\system\management\base_commands.py:21`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\system\management\base_commands.py:40`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\system\management\base_commands.py:62`

### Site settings fixture import needs a singleton/update service seam

Lily's `update_site_settings` command owns generic singleton fixture behavior:
load first fixture item, compare current fields, update changed fields, save,
and sync Redis.

- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_site_settings.py:23`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_site_settings.py:47`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_site_settings.py:70`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\management\commands\update_site_settings.py:72`

The concrete model also defines a local singleton `load()` and a local manager
factory fallback even though the library already has settings sync mixins and
manager factories.

- `C:\install\projects\clients\lily_website\src\lily_backend\system\models\settings.py:88`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\models\settings.py:101`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\system\mixins\settings.py:18`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\system\mixins\settings.py:32`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\system\mixins\settings.py:57`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\system\mixins\settings.py:269`

### Action-token Redis manager is project-local but generally reusable

Lily has a Redis token manager for action confirmation flows. The payload is
booking-shaped, but the mechanics are generic: create secure token, write JSON
with TTL, read/parse, and delete.

- `C:\install\projects\clients\lily_website\src\lily_backend\system\redis.py:11`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\redis.py:19`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\redis.py:28`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\redis.py:46`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\redis.py:61`

Library Redis base keying already supports namespaced managers:

- `C:\install\projects\codex_tools\codex-django\src\codex_django\core\redis\managers\base.py:9`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\core\redis\managers\base.py:17`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\core\redis\managers\base.py:24`

### Client profile selector/service is reusable around the abstract profile

The library provides `AbstractUserProfile`, but Lily still owns generic
get-or-create and simple form save behavior.

- `C:\install\projects\clients\lily_website\src\lily_backend\system\selectors\client_profile.py:15`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\selectors\client_profile.py:17`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\services\client_profile.py:21`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\services\client_profile.py:30`
- `C:\install\projects\clients\lily_website\src\lily_backend\system\services\client_profile.py:45`
- `C:\install\projects\codex_tools\codex-django\src\codex_django\system\mixins\user_profile.py:15`

## 2. Missing library seams

- Generic JSON fixture loader/upserter for Django fixture-like lists.
- Hash-protected command subclass that can import model records by configured
  model, fixture path, lookup field, and optional field transform.
- Singleton settings fixture importer that handles `pk=1`/`load()` style models,
  changed-field detection, save, and Redis sync.
- Aggregate command presentation hook so projects can print section labels while
  still using `BaseUpdateAllContentCommand.handle()` and `--force`.
- Generic Redis JSON action token manager with configurable prefix, token length,
  TTL, and payload validation.
- Optional user-profile selector/service helpers built around a configurable
  profile model and user field mapping.

## 3. Universal vs Project-Specific

Universal behavior suitable for `codex-django`:

- Hash comparison, unchanged-fixture skipping, and fixture hash persistence.
- JSON fixture file loading and validation.
- Upsert by `fields[lookup_field]` with counters and predictable success output.
- Singleton model update from first fixture object with changed-field detection.
- Redis manager sync after a singleton settings update.
- Secure token create/read/delete mechanics with Redis TTL.
- Profile get-or-create from `AUTH_USER_MODEL` and basic payload extraction.

Project-specific behavior to keep in Lily:

- Concrete fixture file locations under `system/fixtures/...`.
- Concrete model classes: `SiteSettings`, `StaticTranslation`, `StaticPageSeo`,
  `EmailContent`, `UserProfile`.
- Static page SEO choices and localized display labels.
- Lily-specific site settings fields such as working hours, hiring text,
  Telegram bot username, booking URL paths, and default logo path.
- Booking-specific action token payload fields and URL returned by
  `AuthService.generate_reschedule_link()`.
- Client privacy/notification preferences and any Lily-specific profile fields.

## 4. Proposed library abstractions

### `JsonFixtureUpsertCommand`

Add a subclass of `BaseHashProtectedCommand` that accepts:

- `fixture_path` or `fixture_paths`
- `model_path` or `model_class`
- `lookup_field`
- `fields_key = "fields"`
- optional `get_defaults(fields)` hook
- optional `get_lookup_value(fields)` hook
- optional `after_save(instance, created, fields)` hook

This should cover static translations, SEO, and email content without each
project reimplementing JSON parsing and counters.

### `SingletonFixtureUpdateCommand`

Add a subclass for one-row settings models:

- resolve model through `model_path` or `CODEX_SITE_SETTINGS_MODEL`
- load singleton through `get_singleton()` defaulting to `objects.get_or_create(pk=1)`
- update only changed fields
- call `save()` only when needed
- call `sync_instance(instance)` hook defaulting to the configured site settings
  Redis manager when available

### Aggregate command section hooks

Extend `BaseUpdateAllContentCommand` with optional hooks:

- `get_command_label(command_name)`
- `before_subcommand(command_name)`
- `after_subcommand(command_name)`

This lets Lily keep readable section output without overriding `handle()`.

### `JsonActionTokenRedisManager`

Add a generic Redis manager under system or core redis:

- `create_token(payload, ttl_seconds | ttl_hours, action_type=None)`
- `get_token_data(token)`
- `delete_token(token)`
- configurable prefix and token factory
- optional payload validator hook

Lily can subclass it for `ActionTokenData` and keep booking-specific fields in
the project.

### User profile helpers

Add a small selector/service layer:

- `get_profile_model(model_path=None)`
- `get_or_create_user_profile(user, defaults_factory=None)`
- `UserProfilePayload`
- `UserProfileService` with overridable field maps

This should stay optional because projects may have custom profile behavior.

## 5. Refactor Candidates

Stage 1: fixture import service primitives

- Add JSON fixture loading and validation helpers.
- Add tests for invalid JSON, invalid shape, missing lookup key, created/updated
  counters, and non-updated hash when import returns `False`.

Stage 2: command subclasses

- Add `JsonFixtureUpsertCommand`.
- Add `SingletonFixtureUpdateCommand`.
- Keep `BaseHashProtectedCommand` backward compatible.
- Add tests using fake models or mocks, not Lily imports.

Stage 3: aggregate command hooks

- Add section-label hooks to `BaseUpdateAllContentCommand`.
- Preserve existing `commands_to_run` behavior and `--force` forwarding.
- Add tests that hooks are called and failures still raise `CommandError`.

Stage 4: generic Redis token manager

- Add a generic JSON token manager with sync methods matching Lily's current
  manager behavior.
- Add tests with mocked Redis client for create/read/delete and malformed JSON.

Stage 5: optional profile helpers

- Add profile get-or-create helpers only if another project shows the same
  pattern, or if Lily cleanup is planned immediately after the command seams.
- Keep this lower priority than fixture/import seams.

## 6. Lily Cleanup List

After a library release with the above seams, Lily can do a project-side cleanup
pass:

- Replace repeated JSON import code in `update_static_translations.py`,
  `update_seo.py`, and `update_email_content.py` with subclasses of
  `JsonFixtureUpsertCommand`.
- Replace `update_site_settings.py` manual singleton update logic with
  `SingletonFixtureUpdateCommand`.
- Remove the `handle()` override from `update_all_content.py`; keep only
  `commands_to_run` and optional section labels so `--force` reaches subcommands.
- Replace local `system.redis.ActionTokenRedisManager` with a project subclass
  of the generic library token manager, keeping Lily's booking payload type.
- Remove the local `get_site_settings_manager()` fallback in
  `system.models.settings` if the updated library factory is sufficient for
  all supported environments.
