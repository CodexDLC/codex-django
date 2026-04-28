# `codex_django.messaging` — Overview

> **Status**: Phase 0 design document. The package described here is the
> rename + expansion of the existing `codex_django.notifications`
> package plus a set of new abstract models lifted from
> `lily_backend.features.conversations`. No code has been written yet.

## Purpose

`codex_django.messaging` is the **Django adapter layer** that bridges
domain code in any codex Django project (lily, future projects) to the
framework-agnostic primitives in `codex_platform.messaging`.

It provides:

* **Abstract Django models** for the four reusable messaging entities
  (system recipient, email log, thread/message, campaign) plus an
  abstract email-settings mixin.
* **Adapters** that fulfill `codex_platform.messaging` protocols using
  Django primitives (`django.core.cache`, `django.utils.translation`,
  the project's ARQ Redis pool).
* **Decorators** for registering project-side email content builders
  in two styles (template / rendered), documented side by side with
  the existing `@notification_handler` registry.
* **A cabinet bridge** for projects that mount a "messaging" cabinet
  module mirroring the booking pattern.

It does not:

* impose concrete model fields beyond a small base set,
* own URL routes or admin classes,
* read configuration from anywhere other than the project's host
  (Django settings + the project's own `EmailSettings` model),
* implement any cabinet UI templates — those live in projects.

## What lives here

| Sub-module | Owns |
|------------|------|
| `messaging.contracts` | `NotificationDispatchSpec`, `QueueAdapterProtocol`, `ContentSelectorProtocol`, `NotificationEventHandler` (existing) plus new `EmailSettingsProtocol` and `AudienceProvider`. |
| `messaging.adapters` | `DjangoArqClient`, `DjangoQueueAdapter`, `DjangoCacheAdapter`, `DjangoI18nAdapter`, `DjangoDirectAdapter` (existing). |
| `messaging.service` | `BaseMessagingEngine` (the `BaseNotificationEngine` rename, with no behavior change). |
| `messaging.builder` | `MessagingPayloadBuilder` (existing `NotificationPayloadBuilder`, renamed). |
| `messaging.selector` | `BaseEmailContentSelector` (existing). |
| `messaging.registry` | `MessagingEventRegistry` + `notification_handler`, `email_template`, `email_rendered` decorators. |
| `messaging.mixins.models` | Abstract models: `AbstractEmailSettings`, `AbstractSystemRecipient`, `AbstractEmailLog`, `AbstractThread`, `AbstractMessage`, `AbstractMessageReply`, `AbstractCampaign`, `AbstractCampaignRecipient`, plus existing `BaseEmailContentMixin`. |
| `messaging.cabinet` | `MessagingBridge` (state DTOs for cabinet panels), `messaging_settings_view` helper. |
| `messaging.audience` | `BaseAudienceBuilder` — Django concrete base implementing `AudienceBuilder` from the platform. |

## Where this package sits

```
codex_platform.messaging  (framework-agnostic core)
        │
        ▼
codex_django.messaging  ← THIS PACKAGE
        │      ├── adapters: bridge platform protocols to Django primitives
        │      ├── mixins.models: abstract Django models projects subclass
        │      ├── service / builder / selector: orchestration on top of platform
        │      ├── registry: event-and-content decorators
        │      └── cabinet: cabinet bridge + settings view helpers
        │
        ▼
project.features.messaging  (concrete models, cabinet routing, project content)
```

## Two-mode design (carried over)

Like its predecessor, `codex_django.messaging` supports the two
delivery modes:

* **Template mode** — `BaseMessagingEngine.dispatch(mode="template",
  template_name=…)`. Worker renders.
* **Rendered mode** — `BaseMessagingEngine.dispatch(mode="rendered",
  html_content=…)`. Host (Django) renders.

The migration adds **decorator-level affordances** for both modes
(see `03_decorators.md`):

* `@email_template("event_key")` — declarative builder for template
  mode.
* `@email_rendered("event_key")` — declarative builder for rendered
  mode.
* `@notification_handler("event_key")` — generic, returns
  `NotificationDispatchSpec` directly (existing API, kept for
  flexibility).

All three end up calling the same `BaseMessagingEngine.dispatch_event`.

## Abstract-model philosophy

Two questions a project asks before subclassing an abstract model:

1. **"Do I need fields beyond what the abstract provides?"** Yes ─►
   subclass and add fields.
2. **"Do I need to override behavior (overrides on `save()`,
   `clean()`, etc.)?"** Yes ─► subclass and override.

If both answers are "no", the project still subclasses to get a
concrete model — the abstract only carries `Meta(abstract=True)`. This
is identical to how `BookingSettings(AbstractBookingSettings)` works
today (`features/booking/booking_settings.py:15`).

Each abstract model documents the minimum fields it provides and the
extension points (overridable methods, computed properties).

## What the project owns

In `lily_backend.features.messaging` (after migration):

* Concrete subclasses of every abstract model.
* `cabinet.py` calling `declare(module="messaging", …)` with the
  project's sidebar items and `settings_url`.
* Project-specific email template builders annotated with
  `@email_template` / `@email_rendered`.
* Project-specific audience filters in `selector/audience.py` (which
  becomes `messaging/selector/audience.py` after rename).

The cabinet UI templates (`templates/cabinet/messaging/...`) live in
the project — `codex_django.messaging` does not ship UI for the same
reason it does not ship URL routes: each project's cabinet has its own
look and structure.

## Open design points (deferred to specific docs)

1. **`@email_template` vs `@email_rendered` vs unified `@notification`** —
   see `03_decorators.md`. Recommendation: split, but both documented.
2. **`Thread` vs `Conversation` naming.** The codex-django abstract is
   `AbstractThread`. Projects may name their concrete model
   `Conversation` for UI purposes. Documented in `01_models_and_mixins.md`.
3. **Audience model coupling.** `BaseAudienceBuilder.materialize()`
   returns `CampaignRecipientDraft` (platform DTO). The Django
   implementation reads from a project-injected client model
   (`CONVERSATIONS_RECIPIENT_MODEL` setting in lily). Documented in
   `06_audience_and_campaigns.md`.

## Naming conventions

| Concept | Library name | Project-side concrete name (suggested) |
|---------|--------------|------------------------------------------|
| Email server / identity settings | `AbstractEmailSettings` | `EmailSettings` |
| Recipients of system notifications | `AbstractSystemRecipient` | `NotificationRecipient` (lily keeps current) |
| Per-send audit row | `AbstractEmailLog` | `EmailLog` |
| Conversation root | `AbstractThread` | `Conversation` (lily) or `Thread` |
| Individual message inside a thread | `AbstractMessage` | `Message` (lily keeps current) |
| Outbound reply to a message | `AbstractMessageReply` | `MessageReply` (lily keeps current) |
| Mass-mailing campaign | `AbstractCampaign` | `Campaign` (lily keeps current) |
| Per-recipient row of a campaign | `AbstractCampaignRecipient` | `CampaignRecipient` (lily keeps current) |

## Referenced documents

* `01_models_and_mixins.md` — abstract model catalog + extension recipes.
* `02_engine_and_dispatch.md` — `BaseMessagingEngine`, two-mode dispatch.
* `03_decorators.md` — `@email_template` / `@email_rendered` / `@notification_handler`.
* `04_cabinet_integration.md` — mirroring booking's cabinet pattern.
* `05_settings_migration.md` — extracting `EmailSettings` from a project's `SiteSettings`.
* `06_audience_and_campaigns.md` — `BaseAudienceBuilder` + campaign callbacks.
