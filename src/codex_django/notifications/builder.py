"""
NotificationPayloadBuilder
==========================
Builds payload dicts for ARQ notification tasks.

Two modes:
- build_template: worker renders Jinja2 template itself (Mode 1)
- build_rendered: payload contains pre-rendered HTML (Mode 2)

Both return plain dicts safe for ARQ serialization.
These dicts correspond to TemplateNotificationDTO and NotificationPayloadDTO
from codex_platform.notifications.dto respectively.
"""

from __future__ import annotations

from typing import Any


class NotificationPayloadBuilder:
    """
    Builds serializable payload dicts for the universal notification task.

    No Django imports — safe to use anywhere.
    """

    def build_template(
        self,
        *,
        notification_id: str,
        recipient_email: str,
        recipient_phone: str | None = None,
        client_name: str = "",
        template_name: str,
        subject: str,
        event_type: str,
        context_data: dict[str, Any],
        channels: list[str],
        language: str = "de",
    ) -> dict[str, Any]:
        """
        Mode 1: worker receives template_name + context_data and renders itself.

        Corresponds to TemplateNotificationDTO in codex_platform.notifications.dto.
        """
        return {
            "mode": "template",
            "notification_id": notification_id,
            "recipient_email": recipient_email,
            "recipient_phone": recipient_phone,
            "client_name": client_name,
            "template_name": template_name,
            "subject": subject,
            "event_type": event_type,
            "context_data": context_data,
            "channels": channels,
            "language": language,
        }

    def build_rendered(
        self,
        *,
        notification_id: str,
        recipient_email: str,
        recipient_phone: str | None = None,
        client_name: str = "",
        html_content: str,
        text_content: str = "",
        subject: str,
        event_type: str,
        channels: list[str],
        language: str = "de",
    ) -> dict[str, Any]:
        """
        Mode 2: payload contains pre-rendered HTML, worker sends as-is.

        Corresponds to NotificationPayloadDTO in codex_platform.notifications.dto.
        """
        return {
            "mode": "rendered",
            "notification_id": notification_id,
            "recipient_email": recipient_email,
            "recipient_phone": recipient_phone,
            "client_name": client_name,
            "html_content": html_content,
            "text_content": text_content,
            "subject": subject,
            "event_type": event_type,
            "channels": channels,
            "language": language,
        }
