"""Reusable audience primitives for messaging campaigns."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from django.apps import apps
from django.conf import settings


@dataclass(frozen=True)
class CampaignRecipientDraft:
    """Portable recipient row for campaign batching."""

    recipient_id: str
    email: str
    first_name: str = ""
    last_name: str = ""
    locale: str = "de"
    unsubscribe_token: str | None = None


class BaseAudienceBuilder:
    """Django base for streaming campaign recipients from a configured model."""

    recipient_model_setting: str = "MESSAGING_RECIPIENT_MODEL"
    legacy_recipient_model_setting: str = "CONVERSATIONS_RECIPIENT_MODEL"
    chunk_size: int = 500

    def __init__(self) -> None:
        model_label = getattr(
            settings,
            self.recipient_model_setting,
            getattr(settings, self.legacy_recipient_model_setting, ""),
        )
        if not model_label:
            raise AttributeError(
                f"Neither {self.recipient_model_setting} nor {self.legacy_recipient_model_setting} is configured"
            )
        self._model = apps.get_model(model_label)

    def base_queryset(self) -> Any:
        """Return the unfiltered base queryset."""
        return self._model.objects.all()

    def apply_filters(self, qs: Any, audience_filter: dict[str, Any]) -> Any:
        """Project override point for custom queryset filtering."""
        return qs

    def to_draft(self, obj: Any) -> CampaignRecipientDraft:
        """Convert one ORM object into a portable recipient draft."""
        return CampaignRecipientDraft(
            recipient_id=str(obj.pk),
            email=str(getattr(obj, "email", "")),
            first_name=str(getattr(obj, "first_name", "")),
            last_name=str(getattr(obj, "last_name", "")),
            locale=str(getattr(obj, "locale", "de")),
            unsubscribe_token=getattr(obj, "unsubscribe_token", None),
        )

    def count(self, audience_filter: dict[str, Any]) -> int:
        """Count recipients after applying project filters."""
        qs = self.apply_filters(self.base_queryset(), audience_filter)
        return int(qs.count())

    def materialize(self, audience_filter: dict[str, Any]) -> Iterator[CampaignRecipientDraft]:
        """Stream recipient drafts in bounded chunks."""
        qs = self.apply_filters(self.base_queryset(), audience_filter)
        for obj in qs.iterator(chunk_size=self.chunk_size):
            yield self.to_draft(obj)


__all__ = ["BaseAudienceBuilder", "CampaignRecipientDraft"]
