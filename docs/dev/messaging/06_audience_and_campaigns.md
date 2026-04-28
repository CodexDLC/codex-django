# Audience and Campaigns

## Goal

Promote `lily_backend.features.conversations.campaigns.audience` and
related dispatcher / batch primitives into reusable
`codex_django.messaging` building blocks. Project-side concrete
audience filters stay in projects.

## Where audience logic lives

| Concept | Layer | What |
|---------|-------|------|
| `AudienceBuilder` Protocol | `codex_platform.messaging.audience` | Framework-agnostic contract: `count`, `materialize`. |
| `BaseAudienceBuilder` | `codex_django.messaging.audience` | Django concrete base — uses `apps.get_model(setting)` to load the project's recipient model; abstract filtering hooks. |
| `LilyAudienceBuilder` | `lily_backend.features.messaging.selector.audience` | Concrete project filters: `consent_marketing`, valid email regex, `appointments__start_time__date__gte`, `appointments__service_id__in`. |
| `CampaignRecipientDraft` | `codex_platform.messaging.dto` | Pydantic DTO carrying per-recipient fields to the worker. |
| `RecipientDraft` (lily) | dataclass in lily today | Will be deleted; replaced by `CampaignRecipientDraft`. |

## `BaseAudienceBuilder`

```python
# src/codex_django/messaging/audience.py
from codex_platform.messaging.audience import AudienceBuilder
from codex_platform.messaging.dto import CampaignRecipientDraft
from django.apps import apps
from django.conf import settings


class BaseAudienceBuilder(AudienceBuilder):
    """Django implementation that streams recipients from a configurable model."""

    recipient_model_setting: str = "MESSAGING_RECIPIENT_MODEL"
    chunk_size: int = 500

    def __init__(self) -> None:
        model_label = getattr(settings, self.recipient_model_setting)
        self._model = apps.get_model(model_label)

    def base_queryset(self):
        return self._model.objects.all()

    def apply_filters(self, qs, audience_filter: dict) -> "QuerySet":
        """Hook for project-specific filters. Default: no-op."""
        return qs

    def to_draft(self, obj) -> CampaignRecipientDraft:
        return CampaignRecipientDraft(
            recipient_id=str(obj.pk),
            email=obj.email,
            first_name=getattr(obj, "first_name", ""),
            last_name=getattr(obj, "last_name", ""),
            locale=getattr(obj, "locale", "de"),
            unsubscribe_token=getattr(obj, "unsubscribe_token", None),
        )

    def count(self, audience_filter: dict) -> int:
        return self.apply_filters(self.base_queryset(), audience_filter).count()

    def materialize(self, audience_filter: dict):
        qs = self.apply_filters(self.base_queryset(), audience_filter)
        for obj in qs.iterator(chunk_size=self.chunk_size):
            yield self.to_draft(obj)
```

The `MESSAGING_RECIPIENT_MODEL` setting (Django) replaces the
lily-specific `CONVERSATIONS_RECIPIENT_MODEL`. The migration aliases
the old name during the deprecation window.

## Project subclass — lily example

```python
# src/lily_backend/features/messaging/selector/audience.py
import re

from codex_django.messaging.audience import BaseAudienceBuilder

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class LilyAudienceBuilder(BaseAudienceBuilder):
    def apply_filters(self, qs, audience_filter):
        f = audience_filter

        if f.get("email_opt_in", True):
            qs = qs.filter(consent_marketing=True, email_opt_out_at__isnull=True)

        if f.get("has_valid_email", True):
            qs = qs.exclude(email="").extra(
                where=["email ~* %s"], params=[EMAIL_REGEX.pattern]
            )

        if locales := f.get("locales"):
            qs = qs.filter(locale__in=locales)

        if since := f.get("has_appointment_since"):
            qs = qs.filter(appointments__start_time__date__gte=since).distinct()

        if service_ids := f.get("service_ids"):
            qs = qs.filter(appointments__service_id__in=service_ids).distinct()

        return qs
```

The `audience_filter` dict shape is project-specific — it ends up in
`Campaign.audience_filter` (JSONField). Documenting the shape is the
project's responsibility (lily docs at
`lily_website/docs/dev/messaging_migration/05_phase_plan.md`).

## Campaign service composition

```python
# src/lily_backend/features/messaging/services/campaign_service.py
from codex_django.messaging.campaigns import CampaignService
from features.messaging.selector.audience import LilyAudienceBuilder
from features.messaging.dispatcher import LilyArqCampaignDispatcher


def build_campaign_service() -> CampaignService:
    return CampaignService(
        audience=LilyAudienceBuilder(),
        dispatcher=LilyArqCampaignDispatcher(),
        locales=["de"],
    )
```

The `CampaignService` (in `codex_django.messaging.campaigns`) is a
straight port of
`features/conversations/services/campaign_service.py:CampaignService`.
The DI shape (`audience`, `dispatcher`, `locales`) is preserved.

## Dispatcher contract

```python
# codex_platform.messaging.campaigns
class CampaignDispatcher(Protocol):
    def enqueue_batch(self, batch: CampaignBatchDTO) -> str: ...
```

Lily's concrete implementation is the existing `ArqCampaignDispatcher`,
renamed `LilyArqCampaignDispatcher` and moved to
`features/messaging/dispatcher.py`:

```python
class LilyArqCampaignDispatcher:
    def enqueue_batch(self, batch: CampaignBatchDTO) -> str:
        from core.arq.client import DjangoArqClient
        return DjangoArqClient().enqueue(
            "send_campaign_batch_task",
            batch.model_dump(mode="json"),
        )
```

## Worker callback path

The worker reports per-recipient status to the URL declared in the
batch (`callback_url`). Today that URL is `/campaigns/recipient-status`
in `features/conversations/api/campaigns.py`. Migration renames it to
`/messaging/campaigns/recipient-status` but keeps the old URL as an
alias during deprecation (so a partially-deployed worker keeps
working).

The endpoint:

1. Validates `callback_token` (today: `OPS_WORKER_API_KEY` scoped to
   `"campaigns.worker"` — see `system/api/auth.py:12-18`).
2. Parses `notification_id` of the form
   `campaign_<campaign_id>_<recipient_pk>`.
3. Calls `CampaignRecipient.objects.filter(pk=recipient_pk).update(...)`.
4. Returns `204 No Content`.

The endpoint MUST be idempotent — the worker can retry callbacks on
network blips.

## Campaign service `send()` contract

`CampaignService.send(campaign)` (async):

1. Materializes `CampaignRecipient` rows from `audience.materialize()`.
2. Batches in groups of 25 (configurable).
3. For each batch:
   * Builds `base_context` with `site_url`, `logo_url` (read from
     `EmailSettings.load()`).
   * Resolves the `EmailTemplate` via
     `messaging.template_registry.get(campaign.template_key)`.
   * Builds a `CampaignBatchDTO`.
   * Calls `dispatcher.enqueue_batch(batch)`.
4. Updates `Campaign.status` from `queued` → `sending` and stores the
   parent ARQ job ID.

`Campaign.status` flips to `done` when every `CampaignRecipient` has
a terminal status (sent | failed | bounced | unsubscribed). The
worker callback handler is responsible for the `done` transition.

## Anti-patterns

* **Loading the entire audience into memory.**
  `BaseAudienceBuilder.materialize` MUST stream via `iterator()`. A
  large campaign with 100K recipients would otherwise OOM the host.
* **Performing send in the parent `send_campaign_batch_task`.** The
  parent task only enqueues per-recipient sub-jobs; this preserves
  bounded job duration and lets ARQ retry per-recipient.
* **Storing the rendered campaign HTML in `Campaign` model.** Templates
  are versioned in code; storing the rendered output in DB makes it
  unclear what the recipient saw if the template later changed. Track
  via `template_key + body_translations`; for audit purposes, rely on
  `EmailLog` rows.
* **Reusing the same `notification_id` for retries.** Each retry gets
  a fresh `notification_id`. The original ID stays in the audit log;
  the recipient correlation lives in
  `CampaignRecipient.arq_job_id` and `EmailLog.notification_id`.
