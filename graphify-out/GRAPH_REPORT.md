# Graph Report - codex-django  (2026-04-28)

## Corpus Check
- 299 files · ~864,448 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4309 nodes · 11350 edges · 67 communities detected
- Extraction: 73% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 3084 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 95|Community 95]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 99|Community 99]]
- [[_COMMUNITY_Community 100|Community 100]]
- [[_COMMUNITY_Community 122|Community 122]]

## God Nodes (most connected - your core abstractions)
1. `Reusable page tracking runtime for codex-django projects.` - 180 edges
2. `BaseDjangoRedisManager` - 91 edges
3. `TableColumn` - 78 edges
4. `js()` - 71 edges
5. `m()` - 66 edges
6. `an()` - 61 edges
7. `filter()` - 58 edges
8. `ns()` - 55 edges
9. `DjangoAvailabilityAdapter` - 52 edges
10. `H()` - 50 edges

## Surprising Connections (you probably didn't know these)
- `Per-provider Redis cache for dashboard data.      Usage in DashboardSelector:` --uses--> `BaseDjangoRedisManager`  [INFERRED]
  src\codex_django\cabinet\redis\managers\dashboard.py → src\codex_django\core\redis\managers\base.py
- `ve()` --calls--> `N()`  [INFERRED]
  src\codex_django\cabinet\static\cabinet\js\vendor\alpine.min.js → src\codex_django\cabinet\static\cabinet\js\vendor\htmx.min.js
- `P()` --calls--> `T()`  [INFERRED]
  src\codex_django\cabinet\static\cabinet\js\vendor\alpine.min.js → src\codex_django\cabinet\static\cabinet\js\vendor\htmx.min.js
- `j()` --calls--> `parse()`  [INFERRED]
  src\codex_django\cabinet\static\cabinet\js\vendor\bootstrap.bundle.min.js → src\codex_django\cabinet\static\cabinet\js\vendor\chart.min.js
- `CacheCoder` --uses--> `Unit tests for :class:`codex_django.cache.values.CacheCoder`.`  [INFERRED]
  src\codex_django\cache\values.py → tests\unit\cache\test_values.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.01
Nodes (250): _(), a(), aa(), addBox(), addElements(), Ae(), afterDatasetsUpdate(), afterDraw() (+242 more)

### Community 1 - "Community 1"
Cohesion: 0.01
Nodes (309): AsyncMock, async_hash(), async_string(), BaseDjangoRedisManager, Skip or execute an import based on the computed fixture hash.          Args:, Synchronize the updated instance to Redis when a manager is available., get_default_redis_manager(), Base Redis manager utilities adapted to Django settings.  This module is the bri (+301 more)

### Community 2 - "Community 2"
Cohesion: 0.01
Nodes (70): _(), a(), Ae(), ao, b(), be(), Bt, c() (+62 more)

### Community 3 - "Community 3"
Cohesion: 0.01
Nodes (141): AbstractBookingSettings, DjangoAvailabilityAdapter, Build a ``BookingEngineRequest`` from DB service/resource data., Build ``MasterAvailability`` dicts from ORM data.          Caches **busy interva, Public seam for project-specific resource ordering policies., Return UTC working hours for a master on a specific date.          Reads from ``, Return UTC break interval for a master on a date., Acquire row-level locks on resource records.          Must be called inside ``tr (+133 more)

### Community 4 - "Community 4"
Cohesion: 0.01
Nodes (211): AbstractBookableAppointment, AppointmentCoreMixin, AppointmentStatusMixin, Meta, codex_django.booking.mixins.appointment ========================================, Appointment lifecycle status.      Status constants are class-level attributes s, Core booking data: when and how long.      Admin fieldsets example::          (_, Convenience base that assembles all appointment mixins.      Usage::          cl (+203 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (203): _(), a(), aa(), Ae(), ai(), an(), Ao(), ar() (+195 more)

### Community 6 - "Community 6"
Cohesion: 0.02
Nodes (163): Return a cached content value by key., ActionSection, BookingChainPreviewData, BookingChainPreviewItem, BookingQuickCreateClientOption, BookingQuickCreateData, BookingQuickCreateServiceOption, BookingSlotPickerData (+155 more)

### Community 7 - "Community 7"
Cohesion: 0.02
Nodes (86): Deprecated compatibility wrapper.  Use ``codex_django.cabinet.notifications`` in, Title(), cabinet(), _cabinet_shell_urls(), _can_use_staff_switch(), _detect_module(), _detect_space(), notifications() (+78 more)

### Community 8 - "Community 8"
Cohesion: 0.03
Nodes (129): _(), a(), Ae(), ar(), B(), bi(), Bn(), br() (+121 more)

### Community 9 - "Community 9"
Cohesion: 0.03
Nodes (82): BaseHashProtectedCommand, BaseUpdateAllContentCommand, FixtureImportResult, JsonFixtureLoadResult, JsonFixtureUpsertCommand, load_json_fixture_rows(), Base classes and helpers for content update and fixture import commands.  These, Register shared command-line arguments.          Args:             parser: Djang (+74 more)

### Community 10 - "Community 10"
Cohesion: 0.03
Nodes (84): PageViewAdmin, Django admin integration for tracking snapshots., Inspect flushed page view snapshots., Cabinet declarations for the reusable tracking app., Install the package in an isolated venv for subprocess-based E2E tests.     Ret, sterile_env(), flush_page_views(), Flush Redis tracking counters into database snapshots. (+76 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (122): m(), _(), A(), ae(), an(), at(), B(), be() (+114 more)

### Community 12 - "Community 12"
Cohesion: 0.03
Nodes (74): ro(), arrayToHash(), balanced(), braceExpand(), childrenIgnored(), cleanUpNextTick(), collectNonEnumProps(), _deepEqual() (+66 more)

### Community 13 - "Community 13"
Cohesion: 0.04
Nodes (50): NotificationPayloadBuilder, NotificationPayloadBuilder ========================== Builds payload dicts for A, Build serializable payload dictionaries for notification queue tasks.      The b, Build a payload where the worker renders the template itself.          Args:, Build a payload that already contains rendered notification content.          Ar, NotificationDispatchSpec, QueueAdapterProtocol, Public contracts for the Django notification integration layer. (+42 more)

### Community 14 - "Community 14"
Cohesion: 0.05
Nodes (41): _ArqAdapterProtocol, build_redis_settings_from_django(), DjangoArqClient, Django-facing ARQ adapter built on top of codex-platform delivery primitives., Minimal protocol expected from the platform ARQ notification adapter., Thin Django-friendly wrapper around codex-platform's ARQ adapter., Lazily create the underlying codex-platform ARQ adapter., Enqueue a task synchronously via the platform ARQ adapter. (+33 more)

### Community 15 - "Community 15"
Cohesion: 0.04
Nodes (70): ABC, Return the model class that receives imported rows., dashboard_view(), DashboardAdapter, DashboardRedisManager, DashboardSelector, extend(), get_context() (+62 more)

### Community 16 - "Community 16"
Cohesion: 0.04
Nodes (57): ActiveMixin, ActiveMixin, BaseEmailContentMixin, Meta, OrderableMixin, Database models for flushed tracking snapshots., Add an ``is_deleted`` flag for soft-deletion workflows.      Notes:         The, Mark the object as deleted without removing the database row.          Notes: (+49 more)

### Community 17 - "Community 17"
Cohesion: 0.06
Nodes (31): cab_initials(), cab_trans(), cab_url(), css_size(), get_item(), is_avatar_url(), jsonify(), optional_static_css() (+23 more)

### Community 18 - "Community 18"
Cohesion: 0.1
Nodes (34): Unit tests for :class:`codex_django.cache.values.CacheCoder`., test_bool_none_enum_path_and_lazy_dump(), test_bytes_roundtrip(), test_date_roundtrip(), test_datetime_roundtrip(), test_decimal_roundtrip_preserves_precision(), test_dump_leaves_unknown_types_as_is(), test_dump_primitives_passthrough() (+26 more)

### Community 19 - "Community 19"
Cohesion: 0.28
Nodes (30): _(), a(), b(), c(), d(), E(), er(), f() (+22 more)

### Community 20 - "Community 20"
Cohesion: 0.11
Nodes (12): Sitemap, BaseSitemap, Sitemap primitives with codex-django defaults.  The base sitemap centralizes can, Sitemap for static route-name pages configured through Django settings., Base sitemap with Codex defaults for multilingual canonical URLs.      The imple, Return the language used for the sitemap ``x-default`` alternate., Build alternate language URLs for a sitemap item.          Args:             ite, Resolve sitemap items to absolute path components.          String items are tre (+4 more)

### Community 21 - "Community 21"
Cohesion: 0.08
Nodes (19): Template tags for multilingual navigation helpers.  The tags in this module are, Translate the current request path into another active language.      Args:, translate_url(), discover_locale_paths(), Helpers for discovering Django locale directories.  Examples:     Resolve locale, Discover locale directories that should be added to ``LOCALE_PATHS``.      The h, Translate the current request path into another active language.      Args:, translate_current_url() (+11 more)

### Community 22 - "Community 22"
Cohesion: 0.11
Nodes (12): AppConfig, CabinetConfig, CodexDjangoConfig, CoreConfig, Django app configuration for the reusable tracking package., Import dashboard providers/declarations after Django app loading., Load ``cabinet.py`` modules from installed apps after startup., Register the tracking runtime and optional cabinet declarations. (+4 more)

### Community 23 - "Community 23"
Cohesion: 0.21
Nodes (13): a(), b(), c(), d(), e(), h(), i(), l() (+5 more)

### Community 24 - "Community 24"
Cohesion: 0.21
Nodes (13): _(), a(), c(), e(), f(), i(), k(), l() (+5 more)

### Community 25 - "Community 25"
Cohesion: 0.21
Nodes (14): _(), a(), d(), e(), f(), i(), l(), m() (+6 more)

### Community 26 - "Community 26"
Cohesion: 0.23
Nodes (14): _(), a(), c(), d(), f(), i(), l(), m() (+6 more)

### Community 27 - "Community 27"
Cohesion: 0.19
Nodes (14): a(), c(), d(), e(), f(), l(), m(), n() (+6 more)

### Community 28 - "Community 28"
Cohesion: 0.15
Nodes (12): AppointmentAggregateAction, AppointmentAggregateData, AppointmentAggregateHeader, AppointmentAggregateItem, AppointmentDisplayData, BookingSummaryData, ClientSelectorData, DateTimePickerData (+4 more)

### Community 29 - "Community 29"
Cohesion: 0.28
Nodes (13): a(), b(), c(), f(), i(), k(), l(), m() (+5 more)

### Community 30 - "Community 30"
Cohesion: 0.23
Nodes (13): a(), c(), e(), f(), i(), l(), m(), o() (+5 more)

### Community 31 - "Community 31"
Cohesion: 0.18
Nodes (12): load_cli_module(), raise_cli_dependency_error(), Import a module from codex_django_cli and normalize missing-dependency errors., Raise a helpful error when the split-out CLI package is unavailable., main(), Lazily dispatch to the real CLI entrypoint from codex-django-cli., _execute_shim(), test_load_cli_module_delegates_to_import_module() (+4 more)

### Community 32 - "Community 32"
Cohesion: 0.21
Nodes (7): _(), i(), l(), n(), s(), t(), u()

### Community 33 - "Community 33"
Cohesion: 0.33
Nodes (10): a(), c(), d(), e(), l(), m(), n(), o() (+2 more)

### Community 34 - "Community 34"
Cohesion: 0.33
Nodes (10): a(), c(), f(), l(), m(), n(), o(), r() (+2 more)

### Community 35 - "Community 35"
Cohesion: 0.24
Nodes (8): compute_file_hash(), compute_paths_hash(), Hash helpers for content and fixture synchronization workflows., Compute a combined SHA-256 digest for multiple fixture files.      The digest in, Compute a SHA-256 digest for a single file.      Args:         path: Filesystem, test_compute_file_hash_changes_with_file_contents(), test_compute_paths_hash_changes_when_filename_changes(), test_compute_paths_hash_ignores_non_files_and_is_name_order_stable()

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (7): a(), c(), e(), i(), s(), t(), u()

### Community 37 - "Community 37"
Cohesion: 0.22
Nodes (1): rs

### Community 38 - "Community 38"
Cohesion: 0.28
Nodes (5): InboxNotificationData, build_inbox_notification_item(), test_build_inbox_notification_item_custom_label_and_icon(), test_build_inbox_notification_item_returns_dict_if_count_positive(), test_build_inbox_notification_item_returns_none_if_count_zero()

### Community 39 - "Community 39"
Cohesion: 0.28
Nodes (8): build_redis_client(), build_redis_service(), namespaced_key(), Shared Redis builders for Django session and cache backends.  Provides the minim, Return an async Redis client with ``decode_responses=True``.      Strings are al, Return a ``RedisService`` bound to an async Redis client., Build a colon-delimited Redis key: ``{PROJECT_NAME}:{prefix}:{key}``.      Empty, _resolve_url()

### Community 40 - "Community 40"
Cohesion: 0.4
Nodes (2): s(), t()

### Community 41 - "Community 41"
Cohesion: 0.33
Nodes (4): BaseCheckRunner, CheckRunner, Quality gate for codex-django., Thin launcher; project policy lives in pyproject.toml.

### Community 42 - "Community 42"
Cohesion: 0.7
Nodes (4): e(), n(), r(), t()

### Community 46 - "Community 46"
Cohesion: 0.67
Nodes (1): Migration

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Generic layout contracts for cabinet UI.  Reserved namespace for future page/hea

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Compatibility shim for the split-out codex-django-cli package.

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Compatibility shim for the split-out codex-django-cli package.

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Compatibility shim for the split-out codex-django-cli package.

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Compatibility shim for the split-out codex-django-cli package.

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Compatibility shim for the split-out codex-django-cli package.

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Compatibility shim for the split-out codex-django-cli package.

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Compatibility shim for the split-out codex-django-cli package.

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Compatibility shim for the split-out codex-django-cli package.

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): Persist the latest booking settings payload to Redis after save.

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (1): Return all registered sections ordered by their display order.

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (1): Return all registered dashboard widgets ordered by their display order.

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (1): Return topbar action declarations in registration order.

### Community 84 - "Community 84"
Cohesion: 1.0
Nodes (1): Return global action declarations in registration order.

### Community 86 - "Community 86"
Cohesion: 1.0
Nodes (1): Return the inclusive number of days in the current period.

### Community 89 - "Community 89"
Cohesion: 1.0
Nodes (1): Encode ``bytes`` as a hex string (roundtrip-safe, ASCII).

### Community 90 - "Community 90"
Cohesion: 1.0
Nodes (1): Best-effort conversion of a nested structure to JSON-native types.          Recu

### Community 92 - "Community 92"
Cohesion: 1.0
Nodes (1): Build ARQ RedisSettings from Django settings as a convenience fallback.

### Community 95 - "Community 95"
Cohesion: 1.0
Nodes (1): Redis expires keys on its own — nothing to sweep.

### Community 98 - "Community 98"
Cohesion: 1.0
Nodes (1): Return whether the fixture file was parsed successfully.

### Community 99 - "Community 99"
Cohesion: 1.0
Nodes (1): Return whether the import completed without fatal errors.

### Community 100 - "Community 100"
Cohesion: 1.0
Nodes (1): Record one page view for the current request.

### Community 122 - "Community 122"
Cohesion: 1.0
Nodes (1): Verify that transaction.on_commit is called with a callback.

## Knowledge Gaps
- **345 isolated node(s):** `Profile header data shown in booking cabinet modals.`, `Single key/value row in a booking modal summary block.`, `Declarative form-field state for booking cabinet modals.`, `Form section state for booking cabinet modals.`, `Resolved booking context extracted from a calendar slot.` (+340 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 37`** (9 nodes): `rs`, `.acquireContext()`, `.addEventListener()`, `.getDevicePixelRatio()`, `.getMaximumSize()`, `.isAttached()`, `.releaseContext()`, `.removeEventListener()`, `.updateConfig()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (6 nodes): `e()`, `n()`, `o()`, `s()`, `t()`, `lunr.da.min.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (3 nodes): `Migration`, `0001_initial.py`, `0001_initial.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (2 nodes): `Generic layout contracts for cabinet UI.  Reserved namespace for future page/hea`, `layout.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (2 nodes): `Compatibility shim for the split-out codex-django-cli package.`, `engine.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (2 nodes): `Compatibility shim for the split-out codex-django-cli package.`, `main.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (2 nodes): `Compatibility shim for the split-out codex-django-cli package.`, `prompts.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (2 nodes): `utils.py`, `Compatibility shim for the split-out codex-django-cli package.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (2 nodes): `Compatibility shim for the split-out codex-django-cli package.`, `add_app.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (2 nodes): `Compatibility shim for the split-out codex-django-cli package.`, `client_cabinet.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (2 nodes): `Compatibility shim for the split-out codex-django-cli package.`, `deploy.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (2 nodes): `Compatibility shim for the split-out codex-django-cli package.`, `quality.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `Persist the latest booking settings payload to Redis after save.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (1 nodes): `Return all registered sections ordered by their display order.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (1 nodes): `Return all registered dashboard widgets ordered by their display order.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (1 nodes): `Return topbar action declarations in registration order.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 84`** (1 nodes): `Return global action declarations in registration order.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 86`** (1 nodes): `Return the inclusive number of days in the current period.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 89`** (1 nodes): `Encode ``bytes`` as a hex string (roundtrip-safe, ASCII).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 90`** (1 nodes): `Best-effort conversion of a nested structure to JSON-native types.          Recu`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 92`** (1 nodes): `Build ARQ RedisSettings from Django settings as a convenience fallback.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 95`** (1 nodes): `Redis expires keys on its own — nothing to sweep.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 98`** (1 nodes): `Return whether the fixture file was parsed successfully.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 99`** (1 nodes): `Return whether the import completed without fatal errors.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 100`** (1 nodes): `Record one page view for the current request.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 122`** (1 nodes): `Verify that transaction.on_commit is called with a callback.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Reusable page tracking runtime for codex-django projects.` connect `Community 4` to `Community 1`, `Community 3`, `Community 6`, `Community 7`, `Community 9`, `Community 10`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 21`, `Community 31`?**
  _High betweenness centrality (0.205) - this node is a cross-community bridge._
- **Why does `filter()` connect `Community 8` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 10`, `Community 11`, `Community 12`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `BaseDjangoRedisManager` connect `Community 1` to `Community 16`, `Community 3`, `Community 4`, `Community 15`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 180 inferred relationships involving `MagicMock` (e.g. with `adapter_models()` and `mock_booking_manager()`) actually correct?**
  _`MagicMock` has 180 INFERRED edges - model-reasoned connections that need verification._
- **Are the 143 inferred relationships involving `Reusable page tracking runtime for codex-django projects.` (e.g. with `BookingActionResult` and `BookingBridge`) actually correct?**
  _`Reusable page tracking runtime for codex-django projects.` has 143 INFERRED edges - model-reasoned connections that need verification._
- **Are the 83 inferred relationships involving `BaseDjangoRedisManager` (e.g. with `_Encoder` and `DashboardRedisManager`) actually correct?**
  _`BaseDjangoRedisManager` has 83 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `TableColumn` (e.g. with `TableFilter` and `TableAction`) actually correct?**
  _`TableColumn` has 76 INFERRED edges - model-reasoned connections that need verification._