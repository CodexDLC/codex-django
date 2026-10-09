"""Reusable campaign batching service contracts."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol

from .audience import BaseAudienceBuilder, CampaignRecipientDraft


@dataclass(frozen=True)
class CampaignBatch:
    """Bounded batch handed to a project-owned dispatcher."""

    campaign_id: str
    recipients: list[CampaignRecipientDraft]
    subject: str
    template_key: str = ""
    locale: str = "de"
    body_text: str = ""
    body_translations: dict[str, str] = field(default_factory=dict)
    audience_filter: dict[str, Any] = field(default_factory=dict)
    base_context: dict[str, Any] = field(default_factory=dict)


class CampaignDispatcherProtocol(Protocol):
    """Minimal dispatcher interface for campaign batch handoff."""

    def enqueue_batch(self, batch: CampaignBatch) -> str: ...


class CampaignService:
    """Compose audience streaming and dispatcher handoff for campaigns."""

    batch_size: int = 25

    def __init__(
        self,
        *,
        audience: BaseAudienceBuilder,
        dispatcher: CampaignDispatcherProtocol,
        locales: Iterable[str] | None = None,
        batch_size: int | None = None,
    ) -> None:
        self._audience = audience
        self._dispatcher = dispatcher
        self._locales = list(locales or ["de"])
        if batch_size is not None:
            self.batch_size = batch_size

    def count_recipients(self, audience_filter: dict[str, Any]) -> int:
        """Return the filtered audience size."""
        return self._audience.count(audience_filter)

    def build_batches(
        self,
        *,
        campaign_id: str,
        subject: str,
        audience_filter: dict[str, Any],
        template_key: str = "",
        locale: str = "de",
        body_text: str = "",
        body_translations: dict[str, str] | None = None,
        base_context: dict[str, Any] | None = None,
    ) -> list[CampaignBatch]:
        """Materialize the audience into bounded dispatcher batches."""
        current: list[CampaignRecipientDraft] = []
        batches: list[CampaignBatch] = []

        for recipient in self._audience.materialize(audience_filter):
            current.append(recipient)
            if len(current) >= self.batch_size:
                batches.append(
                    CampaignBatch(
                        campaign_id=campaign_id,
                        recipients=list(current),
                        subject=subject,
                        template_key=template_key,
                        locale=locale,
                        body_text=body_text,
                        body_translations=dict(body_translations or {}),
                        audience_filter=dict(audience_filter),
                        base_context=dict(base_context or {}),
                    )
                )
                current.clear()

        if current:
            batches.append(
                CampaignBatch(
                    campaign_id=campaign_id,
                    recipients=list(current),
                    subject=subject,
                    template_key=template_key,
                    locale=locale,
                    body_text=body_text,
                    body_translations=dict(body_translations or {}),
                    audience_filter=dict(audience_filter),
                    base_context=dict(base_context or {}),
                )
            )

        return batches

    def send(
        self,
        *,
        campaign_id: str,
        subject: str,
        audience_filter: dict[str, Any],
        template_key: str = "",
        locale: str = "de",
        body_text: str = "",
        body_translations: dict[str, str] | None = None,
        base_context: dict[str, Any] | None = None,
    ) -> list[str]:
        """Build and enqueue all campaign batches."""
        job_ids: list[str] = []
        for batch in self.build_batches(
            campaign_id=campaign_id,
            subject=subject,
            audience_filter=audience_filter,
            template_key=template_key,
            locale=locale,
            body_text=body_text,
            body_translations=body_translations,
            base_context=base_context,
        ):
            job_ids.append(self._dispatcher.enqueue_batch(batch))
        return job_ids


__all__ = ["CampaignBatch", "CampaignDispatcherProtocol", "CampaignService"]
