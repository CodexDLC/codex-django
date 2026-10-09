"""Present messaging cabinet state as reusable cabinet component data."""

from __future__ import annotations

from typing import Any

from codex_django.cabinet import DataTableData, ListRow, SplitPanelData, TableAction, TableColumn, TableFilter

from .types import (
    CampaignComposerState,
    CampaignDetailState,
    CampaignListState,
    CampaignRowState,
    DeliveryLogRowState,
    DeliveryLogState,
    MailboxState,
    MailboxThreadState,
    MessagingSettingsState,
    RecipientListState,
    RecipientRowState,
)


class MessagingCabinetPresenter:
    """Map project-provided messaging states into cabinet template contexts."""

    def mailbox_context(self, state: MailboxState) -> dict[str, Any]:
        return {
            "mailbox": state,
            "mailbox_panel": SplitPanelData(
                items=[self._thread_row(thread) for thread in state.threads],
                active_id=state.selected.thread.id if state.selected and state.selected.thread else "",
                detail_url="",
                empty_message=state.empty_message,
            ),
            "unread_messages_count": sum(1 for thread in state.threads if thread.unread),
        }

    def campaign_list_context(self, state: CampaignListState) -> dict[str, Any]:
        return {"campaigns": state, "campaigns_table": self._campaign_table(state)}

    def campaign_composer_context(self, state: CampaignComposerState) -> dict[str, Any]:
        return {"campaign": state}

    def campaign_detail_context(self, state: CampaignDetailState) -> dict[str, Any]:
        return {"campaign": state}

    def recipient_list_context(self, state: RecipientListState) -> dict[str, Any]:
        return {"recipients": state, "recipients_table": self._recipient_table(state)}

    def delivery_log_context(self, state: DeliveryLogState) -> dict[str, Any]:
        return {"delivery_log": state, "delivery_log_table": self._delivery_table(state)}

    def settings_context(self, state: MessagingSettingsState) -> dict[str, Any]:
        return {"messaging_settings": state}

    @staticmethod
    def _thread_row(thread: MailboxThreadState) -> ListRow:
        secondary_parts = [part for part in [thread.sender_label or thread.sender_name, thread.preview] if part]
        return ListRow(
            id=thread.id,
            primary=thread.subject,
            secondary=" - ".join(secondary_parts),
            meta=thread.received_at,
            avatar=(thread.sender_label or thread.sender_name or thread.sender_email)[:2].upper(),
            url=thread.url,
        )

    @staticmethod
    def _campaign_row(row: CampaignRowState) -> dict[str, Any]:
        status_label = row.status_label or row.status
        return {
            "id": row.id,
            "subject": row.subject,
            "status": row.status,
            "status_label": status_label,
            "locale": row.locale,
            "recipient_count": row.recipient_count,
            "sent_count": row.sent_count,
            "failed_count": row.failed_count,
            "scheduled_at": row.scheduled_at,
            "sent_at": row.sent_at,
            "updated_at": row.updated_at,
            "url": row.url,
            "status_colors": {
                "draft": "secondary",
                "scheduled": "info",
                "sending": "primary",
                "sent": "success",
                "failed": "danger",
                "cancelled": "dark",
            },
        }

    def _campaign_table(self, state: CampaignListState) -> DataTableData:
        return DataTableData(
            columns=[
                TableColumn(key="subject", label="Subject", bold=True),
                TableColumn(key="status_label", label="Status", badge_key="status_colors"),
                TableColumn(key="locale", label="Locale"),
                TableColumn(key="recipient_count", label="Recipients", align="right"),
                TableColumn(key="sent_count", label="Sent", align="right"),
                TableColumn(key="failed_count", label="Failed", align="right"),
                TableColumn(key="updated_at", label="Updated", muted=True),
            ],
            rows=[self._campaign_row(row) for row in state.rows],
            filters=[TableFilter(key=item.key, label=item.label, value=item.key) for item in state.status_filters],
            actions=[TableAction(label="Open", url_key="url", icon="bi-eye")],
            search_placeholder="Search campaigns...",
            empty_message=state.empty_message,
        )

    @staticmethod
    def _recipient_row(row: RecipientRowState) -> dict[str, Any]:
        status = "enabled" if row.enabled else "disabled"
        return {
            "id": row.id,
            "email": row.email,
            "name": row.name,
            "kind": row.kind,
            "locale": row.locale,
            "status": status,
            "enabled_label": "Enabled" if row.enabled else "Disabled",
            "note": row.note,
            "url": row.url,
            "status_colors": {"enabled": "success", "disabled": "secondary"},
        }

    def _recipient_table(self, state: RecipientListState) -> DataTableData:
        return DataTableData(
            columns=[
                TableColumn(key="email", label="Email", bold=True),
                TableColumn(key="name", label="Name"),
                TableColumn(key="kind", label="Kind"),
                TableColumn(key="locale", label="Locale"),
                TableColumn(key="enabled_label", label="Status", badge_key="status_colors"),
                TableColumn(key="note", label="Note", muted=True),
            ],
            rows=[self._recipient_row(row) for row in state.rows],
            filters=list(state.filters),
            actions=[TableAction(label="Open", url_key="url", icon="bi-eye")],
            search_placeholder="Search recipients...",
            empty_message=state.empty_message,
        )

    @staticmethod
    def _delivery_row(row: DeliveryLogRowState) -> dict[str, Any]:
        return {
            "id": row.id,
            "recipient": row.recipient,
            "event_type": row.event_type,
            "channel": row.channel,
            "status": row.status,
            "subject": row.subject,
            "queued_at": row.queued_at,
            "sent_at": row.sent_at,
            "error_message": row.error_message,
            "provider_message_id": row.provider_message_id,
            "status_colors": {
                "queued": "secondary",
                "sent": "success",
                "failed": "danger",
                "bounced": "warning",
                "skipped": "dark",
            },
        }

    def _delivery_table(self, state: DeliveryLogState) -> DataTableData:
        return DataTableData(
            columns=[
                TableColumn(key="recipient", label="Recipient", bold=True),
                TableColumn(key="event_type", label="Event"),
                TableColumn(key="channel", label="Channel"),
                TableColumn(key="status", label="Status", badge_key="status_colors"),
                TableColumn(key="subject", label="Subject"),
                TableColumn(key="sent_at", label="Sent at", muted=True),
                TableColumn(key="error_message", label="Error", muted=True),
            ],
            rows=[self._delivery_row(row) for row in state.rows],
            filters=list(state.filters),
            search_placeholder="Search delivery log...",
            empty_message=state.empty_message,
        )


__all__ = ["MessagingCabinetPresenter"]
