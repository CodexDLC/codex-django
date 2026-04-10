# Lily System Cleanup Note

This note records project-side cleanup that can be done after Lily consumes a
codex-django release containing the System domain refactor seams. Do not apply
these edits during the library-only pass.

Project root:

- `C:\install\projects\clients\lily_website\src\lily_backend`

## Management Commands

Replace repeated JSON fixture import logic with the new library command bases:

- `system\management\commands\update_static_translations.py`
  should subclass `codex_django.system.management.JsonFixtureUpsertCommand`
  with `fixture_key = "static_translations"`, model `system.StaticTranslation`,
  fixture path `system/fixtures/content/static_translations.json`, and
  `lookup_field = "key"`.
- `system\management\commands\update_seo.py`
  should subclass `JsonFixtureUpsertCommand` with
  `fixture_key = "static_pages_seo"`, model `system.StaticPageSeo`, fixture path
  `system/fixtures/seo/static_pages_seo.json`, and `lookup_field = "page_key"`.
- `system\management\commands\update_email_content.py`
  should subclass `JsonFixtureUpsertCommand` with
  `fixture_key = "email_content"`, model `system.EmailContent`, fixture path
  `system/fixtures/content/email_content.json`, and `lookup_field = "key"`.
- `system\management\commands\update_site_settings.py`
  should subclass `codex_django.system.management.SingletonFixtureUpdateCommand`
  with `fixture_key = "site_settings"`, model `system.SiteSettings`, and fixture
  path `system/fixtures/content/site_settings.json`.

Keep Lily-owned fixture paths and model choices in Lily. The library should own
only the generic load, validate, upsert, singleton update, hash, and Redis sync
mechanics.

## Aggregate Content Update

`system\management\commands\update_all_content.py` can remove its custom
`handle()` override after the project moves to the extended
`BaseUpdateAllContentCommand`. Keep `commands_to_run` and optionally override
`get_command_label()` or `before_subcommand()` for readable section output.

This restores `--force` forwarding to all subcommands.

## Action Tokens

`system\redis.py` can replace local secure-token Redis mechanics with a Lily
subclass of `codex_django.system.redis.managers.JsonActionTokenRedisManager`.

Keep project-specific details local:

- `ActionTokenData` payload shape
- booking appointment IDs
- proposed slot serialization
- action type names such as `reschedule`
- URLs returned by `system.services.auth.AuthService`

## Site Settings

After the singleton command migration, review whether the local
`get_site_settings_manager()` fallback in `system\models\settings.py` is still
needed. Prefer the public codex-django manager factory when supported by all
Lily environments.
