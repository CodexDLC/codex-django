# Library Domain Refactor Prompts

Working document for comparing `codex-django` with `lily_backend` domain-by-domain,
finding project-side workarounds, and turning them into proper extension seams in the library.

Primary project for comparison:
- `C:\install\projects\clients\lily_website\src\lily_backend`

Library root:
- `C:\install\projects\codex_tools\codex-django`

## How To Use This File

Work through one domain at a time.

For each domain:
- compare the library domain with the matching project domain
- identify where the project had to copy, wrap, bypass, or monkey-patch library behavior
- separate universal behavior from project-specific policy
- propose library-side extension seams
- implement only library-safe changes
- list what can be deleted or simplified in `lily_backend` after the new library release

Recommended workflow:
1. Pick one domain block below.
2. Use the domain prompt as the starting prompt.
3. Keep the scope to that one domain only.
4. After the library refactor is done, create a short follow-up checklist for the project cleanup.

## Recommended Models

Use these as defaults:

- `GPT-5.4-Mini` + `medium`
  Good for narrow, mechanical cleanup or docs-only passes.
- `GPT-5.4` + `high`
  Default for most domain audits and moderate refactors.
- `GPT-5.3-Codex` + `high`
  Best for deeper codebase refactors, extension seam design, and behavior-preserving API work.

## Domain Board

### 1. Booking

Status:
- [ ] Not started
- [x] Domain audit done
- [x] Universal vs project-specific rules separated
- [x] Library extension seams designed
- [ ] Library code refactored
- [ ] Backward compatibility checked
- [ ] Lily cleanup checklist written

Booking stage tracker:
- [x] Stage 1 done — minimal seams in library (`selectors` helpers, contracts widening, picker types)
- [x] Stage 2 done — lily_backend cleanup and duplicate helper removal
- [x] Stage 3 done — resource prioritization seam
- [x] Stage 4 done — create_booking orchestration seam
- [x] Stage 5 done — gateway cleanup and final Lily checklist

Policy:
- Naming policy: `resource/executor` only (no `master_*` terms in new public seams)
- Compatibility policy: Immediate break now (no aliases)
- Rollout policy: library + lily_backend in one synchronized change set

Final Lily cleanup checklist:
- [x] `features/booking/services/cabinet_availability.py` delegates picker rows and slot payload normalization to library helpers
- [x] project adapter prioritization uses public seam (`prioritize_resource_ids`) instead of private override contract
- [x] local booking orchestration service removed; booking commit flow goes through library `create_booking`
- [x] provider/gateway day-slot fallback uses public gateway seam (`get_resource_day_slots`) with no private adapter access
- [x] targeted lily booking regression tests are green on updated contracts (`cabinet_availability_flow`, `public_scheduler`, `multi_service_slot_limits`, `overlapping`)

Recommended model:
- `GPT-5.3-Codex`

Recommended reasoning:
- `high`

Why:
- This domain already shows project-side wrapper/gateway code, selector duplication, custom creation flow, custom picker logic, and use of internal adapter methods.

Library area:
- `src/codex_django/booking`

Project area:
- `C:\install\projects\clients\lily_website\src\lily_backend\features\booking`

Initial findings to validate:
- project had to create `features/booking/selector`
- project had to wrap library selectors in a custom gateway
- project had to override adapter behavior via internal methods
- project had to reimplement booking creation orchestration
- project had to add project-side picker/calendar service logic

Prompt:

```text
Audit only the booking domain between:
- library: C:\install\projects\codex_tools\codex-django\src\codex_django\booking
- project: C:\install\projects\clients\lily_website\src\lily_backend\features\booking

Goal:
- identify where the project was forced to work around missing library extension points
- separate project-specific policy from universal booking/runtime behavior
- propose and implement library-side extension seams so projects can inherit/override behavior without copying selector logic

Focus on:
- selectors
- engine gateway
- booking creation flow
- adapter extension points
- picker/calendar availability builders
- hooks and persistence seams

Output format:
1. Findings: concrete workaround points with file references
2. Universal behavior to move into library
3. Project-specific behavior to keep in project
4. Proposed library API/classes/protocols
5. Library code changes
6. Post-release cleanup list for lily_backend

Constraints:
- keep the scope to booking only
- prefer base classes / services / protocols over giant standalone functions when projects need overrides
- preserve backward compatibility where possible
```

### 2. Cabinet

Status:
- [x] Not started
- [x] Domain audit done
- [x] Universal vs project-specific rules separated
- [x] Library extension seams designed
- [x] Library code refactored
- [x] Backward compatibility checked
- [x] Lily cleanup checklist written

Cabinet stage tracker:
- [x] Stage 1 done — public registry/runtime read APIs (`configure_space`, `get_space_config`, filtered registry readers)
- [x] Stage 2 done — view customization seams (`CabinetModuleMixin`, `CabinetTemplateView`, staff/owner access mixins)
- [x] Stage 3 done — modal presentation seam (`ModalPresenter`, `present_modal_state`)
- [x] Stage 4 done — site settings hooks for service/model/tab/save/permission customization
- [x] Stage 5 done — component/template knobs for card grids, avatars, client topbar, charts, and date-time labels
- [x] Stage 6 done — booking-cabinet helper seams for availability normalization and workflow payload assembly

Final Lily cleanup checklist:
- [x] project quick-access style UIs can use public registry readers instead of `cabinet_registry._sidebar`
- [x] project cabinet views can inherit library mixins instead of repeating module/template/access setup
- [x] project modal builders can delegate generic section conversion to `ModalPresenter`
- [x] project site-settings flows can override service hooks instead of copying the built-in view/service flow
- [x] project booking cabinet services can use library presenters/workflow helpers for slot payloads and quick-create context
- [x] targeted cabinet and booking-cabinet seam tests are covered in the library

Recommended model:
- `GPT-5.4`

Recommended reasoning:
- `high`

Why:
- Cabinet is broad and UI-heavy. The key question is where the project had to override templates, selectors, view assembly, widget contracts, or service composition because runtime seams were missing.

Library area:
- `src/codex_django/cabinet`

Project area:
- `C:\install\projects\clients\lily_website\src\lily_backend\cabinet`
- `C:\install\projects\clients\lily_website\src\lily_backend\features\booking\services`

Prompt:

```text
Audit only the cabinet domain between:
- library: C:\install\projects\codex_tools\codex-django\src\codex_django\cabinet
- project: C:\install\projects\clients\lily_website\src\lily_backend\cabinet

Also inspect project-side cabinet-adjacent logic under:
- C:\install\projects\clients\lily_website\src\lily_backend\features\booking\services

Goal:
- find where the project had to override templates, widget payloads, selectors, or service assembly because the library cabinet runtime was not sufficiently extensible

Focus on:
- template overrides
- widget contracts
- selector/services split
- view-level customization seams
- registry/configuration points

Output format:
1. Findings with file references
2. Universal cabinet behavior missing in the library
3. Project-specific presentation/business rules that should remain outside the library
4. Proposed extension seams
5. Library-safe refactor plan
6. Lily cleanup list after release

Keep the scope to cabinet only.
```

### 3. Core

Status:
- [ ] Not started
- [x] Domain audit done
- [x] Universal vs project-specific rules separated
- [x] Library extension seams designed
- [x] Library code refactored
- [x] Backward compatibility checked
- [x] Lily cleanup checklist written

Core stage tracker:
- [x] Stage 1 done — sitemap alternates now attach to URL entries and x-default is configurable with `SITEMAP_DEFAULT_LANGUAGE`
- [x] Stage 2 done — `StaticPagesSitemap` provides settings-backed static route sitemap behavior
- [x] Stage 3 done — public i18n URL translation helper backs the template tag
- [x] Stage 4 done — top-level Redis exports include all core managers plus a default manager factory
- [x] Stage 5 done — static-page SEO selector accepts model, lookup field, cache manager, and timeout seams

Final Lily cleanup checklist:
- [ ] delete the project-side `StaticSitemap.get_urls()` override after consuming the updated library
- [ ] replace local `core.templatetags.i18n_urls` usage with the library `codex_i18n` tag/helper
- [ ] replace internal Redis imports/local wrapper with public `codex_django.core.redis` imports or `get_default_redis_manager`
- [ ] keep Lily-owned sitemap settings local: `SITEMAP_STATIC_PAGES`, `SITEMAP_DEFAULT_LANGUAGE`, and `SITEMAP_LOOKUP_NAMESPACES`
- [ ] keep `codex_makemessages` extraction deferred unless another project duplicates management-command planning logic

Recommended model:
- `GPT-5.4`

Recommended reasoning:
- `medium`

Why:
- Core usually contains mixins, helpers, redis managers, i18n, SEO, templatetags, and small infrastructure seams. Lower ambiguity than booking.

Library area:
- `src/codex_django/core`

Project area:
- `C:\install\projects\clients\lily_website\src\lily_backend\core`

Prompt:

```text
Audit only the core domain between:
- library: C:\install\projects\codex_tools\codex-django\src\codex_django\core
- project: C:\install\projects\clients\lily_website\src\lily_backend\core

Goal:
- find places where the project had to duplicate generic infrastructure because the library only exposed internals or low-level helpers

Focus on:
- mixins
- redis managers
- i18n discovery/helpers
- SEO helpers/selectors
- templatetags
- management utilities

Output format:
1. Findings
2. Universal behavior to move up into public library API
3. Project-specific behavior to keep local
4. Proposed extension seams
5. Refactor candidates
6. Post-release cleanup list
```

Follow-up documentation and memory prompt:

```text
Update documentation and memory for the codex-django core refactor.

Scope:
- Library only for code and tests: C:\install\projects\codex_tools\codex-django\src\codex_django\core
- Lily docs only: C:\install\projects\clients\lily_website\docs\en_EN\architecture\backend_django\core\sitemaps.md
- Do not change Lily Python code.
- Do not create a release tag or version section.
- Put changelog notes under CHANGELOG.md [Unreleased].

Documentation tasks:
- Update LIBRARY_DOMAIN_REFACTOR_PROMPTS.md Core board/status and Lily cleanup checklist.
- Update the single Lily sitemap md to describe the new library-backed sitemap behavior and the remaining Lily-owned settings.
- Keep docs concise and avoid moving Lily-specific policy into codex-django docs.

Memory graph tasks:
- Add/update observations that codex-django core now exposes public sitemap seams, StaticPagesSitemap, i18n URL helper, default Redis manager factory/exports, and configurable static SEO selector seams.
- Add/update observations that Lily should later remove local StaticSitemap.get_urls, core.templatetags.i18n_urls, and local core.redis wrapper after consuming the updated library.
```

### 4. System

Status:
- [ ] Not started
- [ ] Domain audit done
- [ ] Universal vs project-specific rules separated
- [ ] Library extension seams designed
- [ ] Library code refactored
- [ ] Backward compatibility checked
- [ ] Lily cleanup checklist written

Recommended model:
- `GPT-5.4`

Recommended reasoning:
- `medium`

Why:
- System tends to contain model mixins, settings, fixture flows, and integration plumbing. Important but usually more structured than booking/cabinet.

Library area:
- `src/codex_django/system`

Project area:
- `C:\install\projects\clients\lily_website\src\lily_backend\system`

Prompt:

```text
Audit only the system domain between:
- library: C:\install\projects\codex_tools\codex-django\src\codex_django\system
- project: C:\install\projects\clients\lily_website\src\lily_backend\system

Goal:
- find where the project had to bypass or extend system/runtime behavior without a clean library seam

Focus on:
- model mixins
- site settings/state management
- redis sync behavior
- fixture/import/export management
- reusable admin/system workflows

Output format:
1. Findings
2. Missing library seams
3. Universal vs project-specific separation
4. Proposed library abstractions
5. Refactor candidates
6. Lily cleanup list
```

### 5. Notifications

Status:
- [ ] Not started
- [ ] Domain audit done
- [ ] Universal vs project-specific rules separated
- [ ] Library extension seams designed
- [ ] Library code refactored
- [ ] Backward compatibility checked
- [ ] Lily cleanup checklist written

Recommended model:
- `GPT-5.4`

Recommended reasoning:
- `high`

Why:
- Notification systems often blur universal dispatch mechanics with project-specific templates, routing, and business triggers.

Library area:
- `src/codex_django/notifications`

Project area:
- `C:\install\projects\clients\lily_website\src\lily_backend\features\conversations`
- `C:\install\projects\clients\lily_website\src\lily_backend\features\booking`

Prompt:

```text
Audit only notification-related runtime seams between:
- library: C:\install\projects\codex_tools\codex-django\src\codex_django\notifications
- project domains that send or orchestrate notifications in lily_backend

Goal:
- determine whether the project is forced to hardcode notification behavior because the library only exposes low-level adapters and not reusable orchestration seams

Focus on:
- dispatch specs
- adapter contracts
- project trigger points
- reusable builder/service patterns
- what belongs in runtime vs what belongs in project templates/business flows

Output format:
1. Findings
2. Universal notification mechanics
3. Project-specific notification policy/content
4. Proposed runtime seams
5. Refactor candidates
6. Lily cleanup list
```

### 6. Conversations

Status:
- [ ] Not started
- [ ] Domain audit done
- [ ] Universal vs project-specific rules separated
- [ ] Library extension seams designed
- [ ] Library code refactored
- [ ] Backward compatibility checked
- [ ] Lily cleanup checklist written

Recommended model:
- `GPT-5.4`

Recommended reasoning:
- `medium`

Why:
- Smaller than booking/cabinet, but still may need clean runtime seams for provider/registry/cabinet integration.

Library area:
- `src/codex_django/conversations`

Project area:
- `C:\install\projects\clients\lily_website\src\lily_backend\features\conversations`

Prompt:

```text
Audit only the conversations domain between:
- library: C:\install\projects\codex_tools\codex-django\src\codex_django\conversations
- project: C:\install\projects\clients\lily_website\src\lily_backend\features\conversations

Goal:
- identify where the project had to rebuild provider/service logic that should have been exposed as a runtime extension seam in the library

Focus on:
- provider interfaces
- cabinet integration
- reusable services/selectors
- domain contracts

Output format:
1. Findings
2. Missing public seams
3. Universal vs project-specific split
4. Proposed library abstractions
5. Refactor candidates
6. Lily cleanup list
```

### 7. Tracking Candidate

Status:
- [ ] Not started
- [ ] Domain audit done
- [ ] Universal vs project-specific rules separated
- [ ] Library-fit decision made
- [ ] Library API drafted
- [ ] Migration plan drafted

Recommended model:
- `GPT-5.3-Codex`

Recommended reasoning:
- `high`

Why:
- This is not just refactoring; it is a domain extraction decision. Need to decide whether `tracking` belongs in the library at all, and if yes, how to package it so projects can wire middleware only.

Project area:
- `C:\install\projects\clients\lily_website\src\lily_backend\tracking`

Expected library target:
- likely a new `src/codex_django/tracking`

Prompt:

```text
Audit the project-only tracking domain as a library extraction candidate:
- project: C:\install\projects\clients\lily_website\src\lily_backend\tracking
- proposed library target: C:\install\projects\codex_tools\codex-django\src\codex_django\tracking

Goal:
- decide whether tracking is generic enough to move into codex-django
- define what the runtime module should own so projects mostly just install the app and connect middleware

Focus on:
- models
- middleware
- recorder/manager/provider separation
- tasks/flush flows
- selector/query layer
- admin integration
- migration/runtime packaging impact

Output format:
1. Generic parts that belong in the library
2. Project-specific parts that must remain overrideable
3. Proposed runtime module structure
4. Public extension seams
5. Migration strategy for lily_backend
6. Release risk notes

Constraint:
- do not assume every project needs the same tracking policy
- design for install-and-wire simplicity plus overrideability
```

## One General Prompt

Use this only when you want a meta-pass before working domain-by-domain.

Recommended model:
- `GPT-5.3-Codex`

Recommended reasoning:
- `high`

Prompt:

```text
Compare codex-django with lily_backend only across domains that overlap or are strong library candidates.

Library root:
- C:\install\projects\codex_tools\codex-django\src\codex_django

Project root:
- C:\install\projects\clients\lily_website\src\lily_backend

Domains to inspect:
- booking
- cabinet
- core
- system
- notifications
- conversations
- tracking (candidate extraction)

Goal:
- produce a domain-by-domain refactor map for improving codex-django as an extensible runtime library
- identify where lily_backend had to add workarounds because library seams were missing

For each domain provide:
1. overlap summary
2. workaround/copy/override points in the project
3. universal behavior that should move into library public API
4. project-specific behavior that should stay local
5. recommended library abstraction style:
   - base class
   - protocol
   - service object
   - registry
   - utility function
6. risk and migration notes
7. recommended next implementation order

Constraint:
- optimize for future library releases that reduce project code without forcing every project into lily-specific business rules
```

## Suggested Execution Order

- [x] Booking
- [x] Cabinet
- [ ] Tracking candidate
- [ ] Core
- [ ] System
- [ ] Notifications
- [ ] Conversations

Why this order:
- `booking` already has confirmed workarounds
- `cabinet` is likely to expose more missing runtime seams
- `tracking` is a fresh extraction candidate and should be designed before ad hoc reuse spreads
- the remaining domains are important, but likely less structurally expensive
