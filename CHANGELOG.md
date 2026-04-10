# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Added public core sitemap seams for alternates, x-default language selection, and settings-backed static page sitemaps.
- Added a public i18n URL translation helper and a default Redis manager factory/export surface.

### Changed

- Changed static-page SEO selection to support injectable model, lookup field, cache manager, and cache timeout seams while preserving existing defaults.

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
