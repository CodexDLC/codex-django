# Changelog

All notable changes to this project will be documented in this file.

## [0.5.3] - 2026-04-19

### Fixed

- Raised the default booking engine solution cap for multi-service availability lookups from 50 to 2000, while preserving the legacy 50 default for single-service requests.
- Propagated the same multi-service default into `create_booking()` final availability revalidation so late-day chain starts do not fail confirmation solely because the revalidation search was truncated.

## [0.5.2] - 2026-04-18

### Added

- Extended `codex_django.cabinet.reports.resolve_report_period` with two new period keys: `"year"` (year-to-date anchored at the current year's January 1st) and `"custom"` (inclusive range supplied via `date_from` / `date_to`, accepting either `date` objects or ISO `YYYY-MM-DD` strings). The comparison window is computed identically to existing periods (same-length block immediately preceding `date_from`).
- `"custom"` with missing or inverted bounds (`date_from > date_to`) falls back to the default `"month"` period so callers can route query-string input through the resolver without pre-validation.
- Report filter templates (`cabinet/includes/_report_filters.html` and the showcase twin) now render a compact `<form method="get">` around the date inputs with a calendar-range submit button. Submitting posts `period=custom&date_from=…&date_to=…` to the same view; the existing period pills continue to drive named periods.

### Changed

- `ReportPeriodKey` type alias broadened to `Literal["week", "month", "quarter", "year", "custom"]`. Callers that narrow the type explicitly must update their annotations.
- Report filter templates now read `date_from` / `date_to` from context (ISO strings) instead of hardcoded `2026-03-01` / `2026-03-31`, and preserve custom bounds across report-tab navigation when `active_period == "custom"`.
- Tracking cabinet declarations now honor `CODEX_TRACKING.track_dashboard_widgets` to allow disabling tracking dashboard widgets without removing the analytics route/topbar/sidebar entry.
- Tracking analytics selectors now apply configured `skip_prefixes` to merged top-pages output and to live Redis multi-day totals before chart summation.

## [0.5.1] - 2026-04-18

### Added

- Added Redis-backed Django session engine `codex_django.sessions.backends.redis.SessionStore`. Stores session payloads as Django-encoded JSON strings (no pickle), uses atomic `SET NX EX` for `must_create`, respects `SESSION_COOKIE_AGE` via `get_expiry_age()`, and propagates `RedisConnectionError` instead of silently returning empty sessions. Namespaced key: `{PROJECT_NAME}:{CODEX_SESSION_KEY_PREFIX}:{session_key}` (prefix defaults to `session`).
- Added Redis-backed Django cache backend `codex_django.cache.backends.redis.RedisCache` implementing the full Django cache contract (`get`, `set`, `add`, `delete`, `get_many`, `set_many`, `delete_many`, `touch`, `has_key`, `incr`, `decr`, `clear`) on top of `codex_platform.redis_service`. Serialization is strict JSON via `codex_django.cache.serializers.JsonSerializer`; pluggable through `OPTIONS["SERIALIZER"]`. `add()` is atomic via `SET NX EX`. `clear()` is namespace-scoped through `SCAN + DEL` on `{KEY_PREFIX}:*` and refuses to run without a non-empty `KEY_PREFIX` — no `FLUSHDB` ever.
- Added `codex_django.cache.values.CacheCoder` with explicit helpers to round-trip `datetime`, `date`, `timedelta`, `Decimal`, `UUID`, `set`, and `bytes` through a JSON cache, plus a recursive `dump()` convenience for nested structures. No magic type tags are stored in Redis — callers decode explicitly.
- Added shared helper `codex_django.core.redis.django_adapter` exposing `build_redis_client`, `build_redis_service`, and `namespaced_key` for backends that need a Redis client without inheriting the `_is_disabled` shortcut of `BaseDjangoRedisManager`.

### Changed

- `docs/dev/django_cache_backend_plan.md` is no longer a forward-looking plan; it now documents the shipped backends, settings wiring, no-pickle policy, and migration path away from `django-redis`.
- **Breaking:** Replaced `SiteEmailSettingsMixin` with `SiteEmailIdentityMixin` in `codex_django.system.mixins`. The new mixin exposes only identity fields (`email_from`, `email_sender_name`, `email_reply_to`) — SMTP transport (host, port, user, password, TLS/SSL flags, SendGrid key) is no longer stored in the database. Configure transport via `EMAIL_*` Django settings / `.env`.
- Rewrote `cabinet/site_settings/partials/_email.html` to render identity-only fields with an info banner pointing at `.env` for transport.
- `DjangoDirectAdapter` now resolves `from_email` as `"<sender_name> <email_from>"` from `SiteSettings` (via the Redis-synced site-settings manager and `CODEX_SITE_SETTINGS_MODEL`), falling back to `DEFAULT_FROM_EMAIL`.
- Updated RU/EN cabinet settings guides to reflect the identity-only email section.

### Removed

- Removed fields `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`, `smtp_use_tls`, `smtp_use_ssl`, `sendgrid_api_key` from `codex_django.system.mixins.settings`. Projects must generate a `RemoveField` migration after upgrading — see the migration notes below.

### Migration

1. Move SMTP credentials from the DB / admin UI into `.env` (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`/`EMAIL_USE_SSL`, `DEFAULT_FROM_EMAIL`).
2. Replace `SiteEmailSettingsMixin` with `SiteEmailIdentityMixin` in your concrete `SiteSettings` model.
3. `python manage.py makemigrations` — expect a `RemoveField` for the 7 removed columns plus `AddField` for `email_from` / `email_sender_name` / `email_reply_to`. If you want to preserve `smtp_from_email`, edit the migration to use `RenameField` for that column before the `RemoveField` batch runs.

### Fixed

- Fixed cabinet widget/report filter templates loading the non-existent `cabinet_extras` tag library; they now load the registered `cabinet_tags` library.
- Fixed cabinet chart widget JSON payload handling so Alpine receives valid `x-data` for regular charts, report charts, and donut charts instead of rendering blank cards.

## [0.4.4] - 2026-04-16

### Added

- Added reusable cabinet report contracts (`ReportPageData`, `ReportChartData`, `ReportTableData`, period helpers) and library report templates for data-driven analytics pages.
- Added dual-axis/mixed dataset support to the cabinet Chart.js widget config.
- Added default cabinet shell URLs for public site, staff/client space switching, login, and logout links, plus safe staff/client topbar navigation that does not require allauth URL names.

## [0.4.3] - 2026-04-16

### Added

- Added `cabinet_vendor_js` block to `base_cabinet.html` to allow flexible overriding or CDN-loading of feature dependencies (like Chart.js).

### Fixed

- Fixed `SiteSettingsService` to correctly handle empty raw values for nullable fields (e.g., `TimeField`, `DateField`) by setting them to `None`.
- Added safety checks for `Chart` existence in `cabinet.js` to prevent runtime errors when the vendor block is modified or missing.

## [0.4.2] - 2026-04-11

### Changed

- Breaking: booking runtime contracts no longer depend on `SiteSettings`; `BookingFeatureModels` now wires only booking-specific models.
- Breaking: booking fallback hours now use a full 7-day `BookingSettings` schedule with `<day>_is_closed`, `work_start_<day>`, and `work_end_<day>` fields.
- Booking availability timezone handling now defaults to `UTC` at runtime, with optional adapter/resource overrides instead of site-settings coupling.
- Updated README and booking documentation to reflect the booking-only runtime boundary and 7-day schedule model.

### Fixed

- Fixed `DjangoAvailabilityAdapter` fallback math so default working hours are read only from `BookingSettings`, never from `SiteSettings`.
- Fixed booking contract and adapter tests to cover closed days, 7-day defaults, and the new runtime timezone behavior.

## [0.4.1] - 2026-04-11

### Fixed

- Fixed Redis key mismatch in `CabinetSettingsRedisManager` by aligning it with the global `site_settings` key.
- Implemented robust database fallback and settings merging in `SiteSettingsService.get_all_settings()` to ensure settings remain available when Redis is offline.
- Updated cabinet context processor to utilize `SiteSettingsService` for unified settings retrieval.

## [0.4.0] - 2026-04-10

### Added

- Added a reusable `tracking` runtime module with models, admin integration, settings, providers, flush helpers, and management commands for page-view analytics.
- Added analytics cabinet integration with selector support, dashboard widgets, middleware-driven recording, and a dedicated analytics view/template surface.
- Added comprehensive unit coverage for tracking runtime flows and notification selector behavior.

### Changed

- Enhanced notification content selection to support cache-prefix aware email lookups.
- Finalized typing and dashboard cleanup around the new tracking and analytics runtime surfaces.

### Fixed

- Fixed runtime test linting issues in the tracking test suite.

## [0.3.2] - 2026-04-10

### Added

- Added public core sitemap seams for alternates, x-default language selection, and settings-backed static page sitemaps.
- Added a public i18n URL translation helper and a default Redis manager factory/export surface.
- Added public system management seams for Django-style JSON fixture upserts, singleton fixture updates, and aggregate command section hooks.
- Added a generic system Redis JSON action-token manager for temporary confirmation/action payloads.
- Added System domain refactor notes and a Lily post-release cleanup note for replacing project-local fixture import and action-token wrappers.

### Changed

- Changed static-page SEO selection to support injectable model, lookup field, cache manager, and cache timeout seams while preserving existing defaults.
- Expanded system documentation around fixture orchestration, singleton settings imports, action-token Redis helpers, and project cleanup boundaries.

### Fixed

- Fixed sitemap alternates being computed but not attached to generated URL entries.

## [0.3.1] - 2026-04-10

### Added

- Added cabinet runtime extension seams: request context resolver, public registry read API, generic view mixins, and modal presenters.
- Added generic booking cabinet helpers for modal presentation, availability normalization, and workflow payload assembly.
- Added component knobs for cabinet card grids, avatars, client topbar hooks, chart widget options, and date-time picker labels.

### Changed

- Updated cabinet context processing and quick-access helpers to use public registry/runtime APIs while preserving existing context keys and template names.
- Made cabinet site settings configurable through service/model/tab/save/permission hooks with default-compatible behavior.

### Fixed

- Removed the need for project code to inspect `cabinet_registry._sidebar` for quick-access-like UIs.

## [0.3.0] - 2026-04-10

### Added

- Cabinet redesign groundwork across templates, styles, quick-access flows, notifications, and dashboard/site-settings surfaces.
- New runtime modules and coverage for conversations, cabinet services/tags, booking contracts, and core app wiring.

### Changed

- Standardized the developer quality gate around `codex_core.dev.check_runner` and moved project policy into `[tool.codex-check]`.
- Raised the runtime dependency floor to the refreshed Codex package line: `codex-core` and `codex-platform` now resolve from `>=0.3.0`, while `codex-services` resolves from the published `>=0.1.3`, all with `<1.0.0` headroom.
- Raised the optional CLI extra to `codex-django-cli>=0.3.0,<0.4.0` so new installs resolve against the current standalone CLI release line.
- Expanded English and Russian docs around cabinet architecture, guides, and settings.
- Booking runtime contracts switched to neutral `resource/executor` naming with public seams for prioritization and orchestration.

### Fixed

- Aligned the cabinet `date_time_picker` month grid by supporting padded calendar cells with leading and trailing blank placeholders.

## [0.2.5] - 2026-03-29

First public release.

### Added

- Optional `cli` extra that installs the published `codex-django-cli` companion package.
- Runtime compatibility shims that forward legacy `codex_django.cli.*` imports to `codex-django-cli`.
- Additional runtime test coverage for dashboard selectors, Redis managers, and showcase views.

### Changed

- Refocused `codex-django` on reusable Django runtime modules while project scaffolding lives in `codex-django-cli`.
- Replaced the old runtime extras layout with `cli`, `dev`, `maintainer`, and `docs`.
- Updated README, install guides, and CI workflow around the runtime/CLI split.
- Reworked the docs landing page into a runtime-oriented entry screen with quick-start paths and module navigation.
- Raised the runtime coverage threshold to reflect the audited baseline.

### Fixed

- Packaging metadata and lockfile resolution for `codex-django[cli]`.
- Online installation flow where a built `codex-django` wheel pulls `codex-django-cli` from the package registry.
- Compatibility typing around the lazy CLI dispatch module.
- Empty integration/e2e marker handling in the maintainer quality gate.
- Async test environment resolution by restoring `arq` and `pytest-asyncio` in development extras.
- Missing `unit` marker coverage for cabinet context processor tests.

## [0.2.0] - Internal milestone

### Added

- Broader runtime modules for cabinet, showcase, booking, system, notifications, and core integrations.
- Expanded unit coverage for runtime helpers and compatibility surfaces.

### Changed

- Reworked the runtime architecture around reusable adapters, mixins, selectors, and generated-project boundaries.
- Evolved scaffold templates and docs in parallel with the runtime modules.

## [0.1.5] - Internal milestone

### Added

- Cabinet/dashboard foundation with selectors, widgets, settings, and templates.
- Showcase reference implementation with mock data, views, and demo flows.
- Booking runtime adapters and selectors.

### Changed

- Extended project templates, feature blueprints, and deployment-oriented repository scaffolds.

## [0.1.0] - Internal milestone

### Added

- Initial library scaffold for Django runtime utilities, mixins, adapters, and Codex-oriented project structure.
