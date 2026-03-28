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
    """Build serializable payload dictionaries for notification queue tasks.

    The builder is framework-agnostic and intentionally avoids Django imports
    so it can be reused in synchronous, asynchronous, and worker contexts.
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
        """Build a payload where the worker renders the template itself.

        Args:
            notification_id: Unique notification identifier.
            recipient_email: Destination email address.
            recipient_phone: Optional phone number for SMS/WhatsApp channels.
            client_name: Optional human-readable recipient name.
            template_name: Worker-side template path to render.
            subject: Localized notification subject.
            event_type: Logical event identifier.
            context_data: Extra template context data.
            channels: Delivery channels requested for the notification.
            language: Language code attached to the payload.

        Returns:
            A plain dictionary compatible with the template-based notification
            DTO expected by the queue worker.
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
        """Build a payload that already contains rendered notification content.

        Args:
            notification_id: Unique notification identifier.
            recipient_email: Destination email address.
            recipient_phone: Optional phone number for SMS/WhatsApp channels.
            client_name: Optional human-readable recipient name.
            html_content: Pre-rendered HTML body.
            text_content: Optional plain-text body.
            subject: Localized notification subject.
            event_type: Logical event identifier.
            channels: Delivery channels requested for the notification.
            language: Language code attached to the payload.

        Returns:
            A plain dictionary compatible with the rendered notification DTO
            expected by the queue worker.
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
