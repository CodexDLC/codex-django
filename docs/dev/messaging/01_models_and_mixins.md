# Abstract Models and Mixins

This document is the catalog of every abstract Django model
`codex_django.messaging` will provide, plus extension recipes. Each
model lists:

* Required fields (with type and rationale).
* Optional fields (with default and rationale).
* Extension hooks (overridable methods, properties).
* Project subclass example.

Existing fields come from `lily_backend.features.conversations.models`
and `lily_backend.features.notifications.models`. Naming is preserved
where neutral; renames are flagged.

## 1. `AbstractEmailSettings`

A singleton model holding the email-identity surface that today is
mixed into `SiteSettings` through `SiteEmailIdentityMixin`. Migration
splits it out (see `05_settings_migration.md`).

### Required fields

```python
email_from         = EmailField(_("From address"))
email_sender_name  = CharField(_("Sender name"), max_length=128)
email_reply_to     = EmailField(_("Reply-To"), blank=True)
site_base_url      = URLField(_("Site base URL"))
logo_url           = CharField(_("Logo URL"), max_length=255, blank=True)
url_path_confirm       = CharField(max_length=255, blank=True)
url_path_cancel        = CharField(max_length=255, blank=True)
url_path_reschedule    = CharField(max_length=255, blank=True)
url_path_contact_form  = CharField(max_length=255, blank=True)
```

### What it does NOT contain

* SMTP credentials (`smtp_host`, `smtp_user`, `smtp_password`). These
  remain env-only by design — see comment in
  `src/lily_backend/core/settings/modules/email.py:1` ("SMTP credentials
  live in environment variables only, never in the database").
* Provider API keys (`SENDGRID_API_KEY`). Same reason.

### Singleton semantics

```python
@classmethod
def load(cls):
    obj, _ = cls.objects.get_or_create(pk=1)
    return obj
```

Identical to `BookingSettings.load()` in
`features/booking/booking_settings.py:53-71`. Projects that need
defaults override `load()`.

### Redis sync

The migration ships a `EmailSettingsSyncMixin` that hooks `post_save`
to push the singleton to a Redis hash named `email_settings:` (the
worker reads it; see
`codex-platform/docs/dev/messaging/05_workers_contract.md`). The hash
key constant lives in `messaging.workers_contract.SETTINGS_HASH_KEY`
so worker and host stay in sync.

### Project subclass

```python
# lily_backend/features/messaging/models/email_settings.py
from codex_django.messaging.mixins import AbstractEmailSettings, EmailSettingsSyncMixin
from django.db import models


class EmailSettings(AbstractEmailSettings, EmailSettingsSyncMixin):
    company_disclaimer_de = models.TextField(blank=True)  # project-specific
    company_disclaimer_en = models.TextField(blank=True)

    class Meta:
        verbose_name = "Email Settings"
        verbose_name_plural = "Email Settings"
```

## 2. `AbstractSystemRecipient`

The library version of the existing
`features/notifications/models/recipient.py:NotificationRecipient`.

### Required fields

```python
email   = EmailField(_("Email"), unique=True)
kind    = CharField(_("Kind"), max_length=32)   # admin, manager, owner...
enabled = BooleanField(_("Enabled"), default=True)
note    = CharField(_("Note"), max_length=255, blank=True)
name    = CharField(_("Name"), max_length=128, blank=True)
```

`kind` is open-ended — projects supply choices via `KIND_CHOICES` on
the subclass.

### Manager helpers

```python
class SystemRecipientManager(models.Manager):
    def enabled_for(self, kind: str) -> "QuerySet[SystemRecipient]":
        return self.filter(enabled=True, kind=kind)
```

Used by host to fetch admin recipients in the compose flow + alerts
flow.

### Project subclass

```python
class NotificationRecipient(AbstractSystemRecipient):
    KIND_CHOICES = [("admin", "Admin"), ("manager", "Manager")]
    kind = models.CharField(max_length=32, choices=KIND_CHOICES)

    class Meta:
        verbose_name = "Notification Recipient"
```

## 3. `AbstractEmailLog`

Replaces the existing `NotificationLog`
(`features/notifications/models/log.py`) and adds a small set of fields
required by the new worker callback contract.

### Required fields

```python
notification_id   = CharField(max_length=128, unique=True, db_index=True)
event_type        = CharField(max_length=128, db_index=True)
channel           = CharField(max_length=32)         # 'email', 'sms', ...
recipient         = CharField(max_length=255)         # email or phone
status            = CharField(max_length=16, db_index=True)  # queued, sent, failed, bounced, unsubscribed
subject           = CharField(max_length=255, blank=True)
error_message     = TextField(blank=True)
context_preview   = JSONField(blank=True, null=True)  # masked subset of context_data
provider_message_id = CharField(max_length=128, blank=True)
message_id_header = CharField(max_length=255, blank=True)  # RFC 5322 Message-ID
queued_at         = DateTimeField(auto_now_add=True)
sent_at           = DateTimeField(null=True, blank=True)
```

### Status state machine

```
queued ─► sent
   │
   ├──► failed   (after retries exhausted)
   │
   └──► bounced  (hard bounce reported by provider)
   │
   └──► unsubscribed (recipient opted out before send)
```

Transitions are write-once — the worker callback inserts or updates a
row keyed by `notification_id`.

### Idempotent upsert

```python
class EmailLogManager(models.Manager):
    def record_status(self, *, notification_id, status, error="", ...):
        obj, _ = self.update_or_create(
            notification_id=notification_id,
            defaults={...},
        )
        return obj
```

The host's `/messaging/notifications/status` endpoint calls this
manager method.

## 4. `AbstractThread`

Conversation root. Lily today calls this `Message` plus a
`thread_key` field; the migration splits the thread aggregate from
the per-message rows.

> **Naming**: lily concrete name remains `Conversation` (matches the
> cabinet sidebar and existing UI). The library abstract is
> `AbstractThread` so other projects can call it whatever fits.

### Required fields

```python
thread_key       = CharField(max_length=64, unique=True, db_index=True)
subject          = CharField(max_length=255, blank=True)
status           = CharField(max_length=16, default="open")
                   # open, processed, spam, archived
last_activity_at = DateTimeField(auto_now=True)
created_at       = DateTimeField(auto_now_add=True)
```

### What's NOT here

The originator (sender_email, sender_name, topic) lives on the first
`AbstractMessage` row, not on the thread. This is the structural
change vs. lily's current model: today, `Message` carries both
"thread root" identity and "individual message" content. The
migration cleanly separates them.

### Migration note

Lily's existing `Message.thread_key` becomes `Conversation.thread_key`.
The first `Message` of a thread keeps `sender_*`/`subject`/`body`. A
data migration walks current `Message` rows, creates a `Conversation`
per unique `thread_key`, and updates FK on `Message`.

## 5. `AbstractMessage`

A single message inside a thread (inbound or outbound).

### Required fields

```python
thread          = ForeignKey(<Thread model>, on_delete=CASCADE, related_name="messages")
direction       = CharField(max_length=16)   # inbound, outbound
sender_name     = CharField(max_length=128, blank=True)
sender_email    = EmailField()
recipient_email = EmailField(blank=True)
subject         = CharField(max_length=255, blank=True)
body            = TextField()
source          = CharField(max_length=32)   # contact_form, email_import, manual, ...
channel         = CharField(max_length=32, default="email")
message_id_header = CharField(max_length=255, blank=True, db_index=True)
in_reply_to_header = CharField(max_length=255, blank=True)
references_header  = TextField(blank=True)   # serialized list
created_at      = DateTimeField(auto_now_add=True)
updated_at      = DateTimeField(auto_now=True)
```

### Project extensions

Lily today adds: `topic` (general, booking, support, feedback, other),
`is_read`, `is_archived`, `dsgvo_consent`, `consent_marketing`, `lang`,
`admin_notes`. These remain project-specific.

## 6. `AbstractMessageReply`

> **Open question** (from approved plan): merge with `AbstractMessage`?
> Recommendation: keep as a separate abstract for now because
> replies have a different invariant — they are always outbound and
> always linked to a parent message. Merging adds a nullable
> `parent_message` FK to `AbstractMessage` and re-creates the same
> issue we're trying to solve.

### Required fields

```python
message     = ForeignKey(<Message model>, on_delete=CASCADE, related_name="replies")
body        = TextField()
sent_by     = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
is_inbound  = BooleanField(default=False)   # True = parsed from inbound mail
created_at  = DateTimeField(auto_now_add=True)
```

## 7. `AbstractCampaign`

### Required fields

```python
created_by         = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
subject            = CharField(max_length=255)
body_text          = TextField(blank=True)
template_key       = CharField(max_length=128, blank=True)
locale             = CharField(max_length=8, default="de")
body_translations  = JSONField(default=dict, blank=True)
audience_filter    = JSONField(default=dict)         # see AudienceBuilder
status             = CharField(max_length=16, default="draft")
                     # draft, queued, sending, done, failed
send_at            = DateTimeField(null=True, blank=True)
sent_at            = DateTimeField(null=True, blank=True)
arq_parent_job_id  = CharField(max_length=128, blank=True)
created_at         = DateTimeField(auto_now_add=True)
updated_at         = DateTimeField(auto_now=True)
```

### Project extensions

Lily-specific `is_marketing` flag stays project-side.

## 8. `AbstractCampaignRecipient`

```python
campaign         = ForeignKey(<Campaign model>, on_delete=CASCADE, related_name="recipients")
recipient        = ForeignKey(settings.CONVERSATIONS_RECIPIENT_MODEL, on_delete=CASCADE)
                   # Lily-specific setting; abstract uses string ref
email            = EmailField()
first_name       = CharField(max_length=128, blank=True)
last_name        = CharField(max_length=128, blank=True)
locale           = CharField(max_length=8, default="de")
status           = CharField(max_length=16, default="pending")
                   # pending, sent, failed, bounced, unsubscribed
arq_job_id       = CharField(max_length=128, blank=True)
sent_at          = DateTimeField(null=True, blank=True)
error            = TextField(blank=True)

class Meta:
    abstract = True
    unique_together = [("campaign", "recipient")]
    indexes = [models.Index(fields=["campaign", "status"])]
```

The `CONVERSATIONS_RECIPIENT_MODEL` Django setting (lily-specific
today) becomes a documented extension point: the abstract uses a
string FK target so projects without a separate "client" model can
point it at `auth.User`.

## 9. Existing: `BaseEmailContentMixin`

Unchanged from `notifications`. Continues to back the database table
that stores localized subject/body strings keyed by content key.

## Migration table

| Lily today | codex-django.messaging abstract | Notes |
|------------|---------------------------------|-------|
| `features/notifications/models/log.py:NotificationLog` | `AbstractEmailLog` | Renamed; gain `notification_id` unique + `provider_message_id`. |
| `features/notifications/models/recipient.py:NotificationRecipient` | `AbstractSystemRecipient` | 1:1 fields. |
| `features/conversations/models/message.py:Message` | `AbstractThread` + `AbstractMessage` | Split: thread vs. message. |
| `features/conversations/models/reply.py:MessageReply` | `AbstractMessageReply` | 1:1 fields. |
| `features/conversations/models/campaign.py:Campaign` | `AbstractCampaign` | 1:1 fields. |
| `features/conversations/models/campaign.py:CampaignRecipient` | `AbstractCampaignRecipient` | 1:1 fields. |
| `features/conversations/models/EmailContent` (already abstract) | `BaseEmailContentMixin` | unchanged. |
| `system/models/settings.py:SiteEmailIdentityMixin` | `AbstractEmailSettings` | Promoted to standalone singleton. |

## Anti-patterns

* **Adding a `body_html` to `AbstractMessage`.** Storing rendered HTML
  in DB couples a model to a presentation layer; if the template
  changes, history is wrong. Store the source (text body + template
  key + context).
* **Computing `thread_key` in views.** The model `save()` (or a custom
  manager) MUST be the only place that issues a thread_key. The
  helper `messaging.threading.build_thread_key()` is the canonical
  generator.
* **Storing SMTP credentials on `EmailSettings`.** Project must
  resist; secrets stay in env. The migration enforces this via
  documentation and a code review checklist; there is no runtime
  enforcement.
