<!-- DOC_TYPE: PROMPT -->

# Public Library Hardening Prompt

Use this prompt for the next deeper pass on `codex-django` public-library
quality. The goal is not to add product features; it is to reduce friction for
external consumers and make the package easier to trust outside the internal
Codex/Lily stack.

## Context Already Handled

The following points from the earlier library audit are already handled or
intentionally deferred:

1. Redis backend recovery tracks B/C/D are complete.
   - `BaseDjangoRedisManager` exposes `sync_string()`, `sync_hash()`,
     `async_string()`, and `async_hash()` context managers.
   - Sync Django cache/session paths no longer go through `async_to_sync`.
   - `codex-platform>=0.4.0,<1.0.0` is required.
2. Core dependency cleanup is complete.
   - `django-debug-toolbar` is not a runtime dependency.
   - `django-unfold` lives in the `admin` extra.
   - `django-prometheus` lives in the `observability` extra.
   - Full local gate uses the `maintainer` extra.
3. Do not remove `codex_django.cabinet.__getattr__` with a direct import-only
   replacement in the current package shape.
   - `codex_django.cabinet` is also a Django app package.
   - Directly importing cabinet view mixins from `cabinet/__init__.py` imports
     `django.contrib.auth.mixins` during `apps.populate()`.
   - That can raise `django.core.exceptions.AppRegistryNotReady`.
   - Removing the lazy export requires a separate app/public-API boundary split.

## Objective

Bring `codex-django` closer to a public PyPI-quality alpha by addressing the
remaining audit concerns in this order:

1. Add behavior-oriented integration coverage for critical runtime flows.
2. Create a settings reference that lists every Django setting read by the
   library.
3. Create a cabinet component catalog for reusable templates/contracts.
4. Define and start a registry v1/v2 compatibility deprecation strategy.
5. Plan, then optionally begin, the cabinet CSS decomposition.
6. Design the safe path for removing lazy public exports from
   `codex_django.cabinet`.

Do not mix unrelated feature work into this pass.

## Non-Negotiable Constraints

- Preserve existing public imports unless the changelog explicitly marks a
  deprecation or breaking change.
- Do not remove the Redis `sync_*`/`async_*` manager contract.
- Do not reintroduce `async_to_sync` into Redis-backed sync Django paths.
- Do not move debug/admin/metrics packages back into core dependencies.
- Keep tests compatible with the existing Windows + `uv` workflow.
- Avoid broad CSS rewrites unless visual verification is added.

## Suggested Execution Plan

### Phase 1: Integration Tests

Add high-signal integration tests that assert behavior, not internal method
calls. Start with flows that matter to downstream projects:

- Redis cache backend:
  - `set/get/add/incr/touch/clear` behavior through Django's cache API.
  - JSON serializer failure for non-JSON values.
  - namespace-scoped `clear()` refusal without `KEY_PREFIX`.
- Redis session backend:
  - save/load/delete lifecycle through Django session store API.
  - expiry semantics using `SESSION_COOKIE_AGE`.
  - collision behavior for `must_create`.
- Cabinet runtime:
  - declared topbar/sidebar entries appear in context for staff/client spaces.
  - quick-access selection is reflected in resolved context.
- Booking availability:
  - prefer one behavior test around `DjangoAvailabilityAdapter` with minimal
    concrete Django models instead of patching the calculator core.

Acceptance:

- Tests should fail if the public behavior changes, not merely if internal
  calls are renamed.
- Existing unit tests may remain, but new coverage must be behavior-first.

### Phase 2: Settings Reference

Create a documentation page that lists all settings read by `codex-django`.
Use `rg "getattr\\(settings|settings\\." src/codex_django` as the source of
truth, then manually group settings by module.

Expected groups:

- Redis/cache/session
- Cabinet runtime and URLs
- Site settings/static content
- SEO
- Tracking
- Notifications/ARQ
- Booking
- Encryption/integrations

Each setting entry should include:

- Name
- Default
- Type/shape
- Module that reads it
- Runtime effect
- Whether it is safe for production defaults

Add the page to both EN and RU docs if the existing docs structure expects
bilingual guide coverage.

### Phase 3: Cabinet Component Catalog

Create a catalog page for reusable cabinet contracts/templates. It should cover
at least:

- `DataTableData`
- `CalendarGridData`
- `CardGridData`
- `ListViewData`
- `SplitPanelData`
- `ModalContentData`
- report contracts under `codex_django.cabinet.reports`

For each component:

- Show the Python contract import.
- Show a minimal payload example.
- Name the template that renders it.
- State what the project owns versus what the library owns.

Do not describe UI keyboard shortcuts or internal visual implementation details
unless they are part of the public contract.

### Phase 4: Registry Compatibility Strategy

Audit `src/codex_django/cabinet/registry.py` and document the v1/v2 split:

- `_sections`
- `_sidebar`
- `_topbar_entries`
- `_module_spaces`
- `declare()` runtime detection

Then choose one of two paths:

1. Documented deprecation only:
   - Add warnings for legacy v1 registration paths.
   - Add changelog notes and migration examples.
2. Internal consolidation:
   - Keep public APIs stable.
   - Store data in one canonical shape.
   - Adapt legacy reads/writes through small compatibility functions.

Acceptance:

- Existing downstream imports and declarations still work.
- Tests cover both legacy and modern declarations.
- The changelog clearly states what is deprecated and what remains supported.

### Phase 5: CSS Decomposition Plan

Do not start with a broad rewrite. First create a plan that maps selectors in
`cab_components.css` to component files.

Suggested target:

- `cab_components/base.css`
- `cab_components/data_table.css`
- `cab_components/calendar.css`
- `cab_components/cards.css`
- `cab_components/list_view.css`
- `cab_components/modal.css`
- `cab_components/reports.css`

Acceptance before merging CSS changes:

- Compiled output remains equivalent or intentionally documented.
- Existing templates render without missing classes.
- Visual smoke checks are added if the project has browser tooling available.

### Phase 6: Cabinet Public API Boundary

Design a safe replacement for `cabinet.__getattr__` before implementing it.

Possible direction:

- Keep `codex_django.cabinet` as the Django app package.
- Introduce a separate public API module such as
  `codex_django.cabinet.api` or `codex_django.cabinet.public`.
- Re-export safe dataclass contracts from `cabinet/__init__.py`.
- Move Django view mixins to the new public API module or document direct
  imports from `codex_django.cabinet.mixins`.
- Add deprecation guidance for lazy mixin access from `codex_django.cabinet`.

Acceptance:

- `django.setup()` succeeds with `codex_django.cabinet` in `INSTALLED_APPS`.
- Static analyzers can discover the recommended public imports.
- Old imports either keep working or emit a clear deprecation warning.

## Verification Commands

Run from the repository root:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv sync --extra maintainer
uv run python tools\dev\check.py --ci
```

For docs-heavy changes also run:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv sync --extra maintainer --extra docs
uv run mkdocs build --clean
```

## Expected Deliverables

- Focused commits, ideally one commit per phase.
- Updated `CHANGELOG.md` for every public behavior, dependency, or docs-policy
  change.
- Updated memory graph entries for stable architectural decisions.
- No release tag unless explicitly requested.
