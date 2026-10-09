"""Reusable abstract Django models for messaging integrations."""

from __future__ import annotations

import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_lifecycle import AFTER_SAVE, LifecycleModelMixin, hook

from ..adapters.email_settings import get_email_settings_manager

log = logging.getLogger(__name__)


class BaseEmailContentMixin(models.Model):
    """Abstract model for storing email and messaging content blocks."""

    CATEGORY_CHOICES: list[tuple[str, str]] = []

    key = models.CharField(_("Key"), max_length=100, unique=True, db_index=True)
    category = models.CharField(_("Category"), max_length=64, blank=True, db_index=True)
    text = models.TextField(_("Text Content"))
    description = models.CharField(_("Description"), max_length=255, blank=True)

    class Meta:
        abstract = True
        ordering = ["category", "key"]

    def __str__(self) -> str:
        return f"[{self.category}] {self.key}"


class AbstractEmailSettings(models.Model):
    """Reusable email identity and URL settings singleton."""

    email_from = models.EmailField(_("From address"))
    email_sender_name = models.CharField(_("Sender name"), max_length=128)
    email_reply_to = models.EmailField(_("Reply-To"), blank=True)
    site_base_url = models.URLField(_("Site base URL"))
    logo_url = models.CharField(_("Logo URL"), max_length=255, blank=True)
    url_path_confirm = models.CharField(_("Confirm URL path"), max_length=255, blank=True)
    url_path_cancel = models.CharField(_("Cancel URL path"), max_length=255, blank=True)
    url_path_reschedule = models.CharField(_("Reschedule URL path"), max_length=255, blank=True)
    url_path_contact_form = models.CharField(_("Contact form URL path"), max_length=255, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def load(cls) -> AbstractEmailSettings:
        """Load or create the singleton settings row."""
        obj, _created = cls._default_manager.get_or_create(pk=1)
        return obj

    def to_redis_dict(self) -> dict[str, str | None]:
        """Serialize concrete scalar fields for Redis storage."""
        data: dict[str, str | None] = {}
        for field in self._meta.get_fields():
            if field.concrete and not field.many_to_many and not field.one_to_many:
                if field.name in {"id", "pk"}:
                    continue
                value = getattr(self, field.name)
                data[field.name] = str(value) if value is not None else None
        return data


class EmailSettingsSyncMixin(LifecycleModelMixin, models.Model):
    """Sync email settings to Redis after save without blocking DB writes."""

    class Meta:
        abstract = True

    @hook(AFTER_SAVE)  # type: ignore[untyped-decorator]
    def sync_email_settings_to_redis(self) -> None:
        if settings.DEBUG and not getattr(settings, "CODEX_REDIS_ENABLED", False):
            return
        if not hasattr(self, "to_redis_dict"):
            return

        try:
            data = self.to_redis_dict()
            if data:
                get_email_settings_manager().sync(data)
        except Exception:
            log.warning("Failed to sync email settings to Redis", exc_info=True)


class AbstractSystemRecipient(models.Model):
    """Recipient entry for system-driven messaging flows."""

    email = models.EmailField(_("Email"), unique=True)
    kind = models.CharField(_("Kind"), max_length=32)
    enabled = models.BooleanField(_("Enabled"), default=True)
    note = models.CharField(_("Note"), max_length=255, blank=True)
    name = models.CharField(_("Name"), max_length=128, blank=True)

    class Meta:
        abstract = True


class AbstractEmailLog(models.Model):
    """Per-send audit row updated by host callbacks or workers."""

    notification_id = models.CharField(max_length=128, unique=True, db_index=True)
    event_type = models.CharField(max_length=128, db_index=True)
    channel = models.CharField(max_length=32)
    recipient = models.CharField(max_length=255)
    status = models.CharField(max_length=16, db_index=True)
    subject = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    context_preview = models.JSONField(blank=True, null=True)
    provider_message_id = models.CharField(max_length=128, blank=True)
    message_id_header = models.CharField(max_length=255, blank=True)
    queued_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class AbstractThread(models.Model):
    """Conversation root for message threads."""

    thread_key = models.CharField(max_length=64, unique=True, db_index=True)
    subject = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, default="open")
    last_activity_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AbstractMessage(models.Model):
    """Single inbound or outbound message within a thread."""

    thread = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="thread_messages")
    direction = models.CharField(max_length=16)
    sender_name = models.CharField(max_length=128, blank=True)
    sender_email = models.EmailField()
    recipient_email = models.EmailField(blank=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    source = models.CharField(max_length=32)
    channel = models.CharField(max_length=32, default="email")
    message_id_header = models.CharField(max_length=255, blank=True, db_index=True)
    in_reply_to_header = models.CharField(max_length=255, blank=True)
    references_header = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AbstractMessageReply(models.Model):
    """Explicit outbound-or-imported reply entry attached to a message."""

    message = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="message_replies")
    body = models.TextField()
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    is_inbound = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AbstractCampaign(models.Model):
    """Mass-mailing campaign metadata."""

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    subject = models.CharField(max_length=255)
    body_text = models.TextField(blank=True)
    template_key = models.CharField(max_length=128, blank=True)
    locale = models.CharField(max_length=8, default="de")
    body_translations = models.JSONField(default=dict, blank=True)
    audience_filter = models.JSONField(default=dict)
    status = models.CharField(max_length=16, default="draft")
    send_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    arq_parent_job_id = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AbstractCampaignRecipient(models.Model):
    """Per-recipient delivery state for one campaign."""

    campaign = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="campaign_recipients",
    )
    recipient_id = models.CharField(max_length=64, db_index=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    locale = models.CharField(max_length=8, default="de")
    status = models.CharField(max_length=16, default="queued", db_index=True)
    notification_id = models.CharField(max_length=128, blank=True, db_index=True)
    error_message = models.TextField(blank=True)
    provider_message_id = models.CharField(max_length=128, blank=True)
    unsubscribe_token = models.CharField(max_length=128, blank=True)
    arq_job_id = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
