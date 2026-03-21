"""
BaseNotificationEngine
======================
Orchestrates notification dispatch: resolves subject, builds payload,
enqueues via the configured adapter.

Subclass this in your project and add send_* methods for your events::

    from codex_django.notifications import (
        BaseNotificationEngine,
        NotificationPayloadBuilder,
        DjangoQueueAdapter,
        DjangoCacheAdapter,
        DjangoI18nAdapter,
        BaseEmailContentSelector,
    )

    class NotificationService(BaseNotificationEngine):
        def send_booking_confirmed(self, booking):
            self.dispatch(
                recipient_email=booking.client_email,
                template_name="emails/booking_confirmed.html",
                event_type="booking_confirmed",
                channels=["email"],
                language="de",
                subject_key="booking_confirmed_subject",
                booking=booking,
            )
"""

from __future__ import annotations

import uuid
from typing import Any, Protocol

from .builder import NotificationPayloadBuilder


class QueueAdapterProtocol(Protocol):
    def enqueue(self, task_name: str, payload: dict[str, Any]) -> str | None: ...
    async def aenqueue(self, task_name: str, payload: dict[str, Any]) -> str | None: ...


class BaseNotificationEngine:
    """
    Wires together selector, builder, and queue adapter to dispatch notifications.

    task_name: name of the ARQ task that handles delivery.
    mode: "template" (worker renders Jinja2) or "rendered" (pre-rendered HTML).
          Override per-dispatch via the `mode` kwarg in dispatch().
    """

    task_name: str = "send_universal_notification_task"
    mode: str = "template"  # default mode for all dispatch() calls

    def __init__(
        self,
        queue_adapter: QueueAdapterProtocol,
        cache_adapter: Any,
        i18n_adapter: Any,
        selector: Any,
    ) -> None:
        self._queue = queue_adapter
        self._cache = cache_adapter
        self._i18n = i18n_adapter
        self._selector = selector
        self._builder = _get_builder()

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def dispatch(
        self,
        *,
        recipient_email: str,
        recipient_phone: str | None = None,
        client_name: str = "",
        template_name: str = "",
        event_type: str,
        channels: list[str],
        language: str = "de",
        subject_key: str,
        mode: str | None = None,
        # Mode 2 only:
        html_content: str = "",
        text_content: str = "",
        **context: Any,
    ) -> str | None:
        """
        Resolve subject, build payload, enqueue.

        mode="template" (default): passes template_name + context to worker.
        mode="rendered": passes pre-rendered html_content to worker.

        Returns job_id or None (when using on_commit adapter).
        """
        effective_mode = mode or self.mode

        subject = self._selector.get(subject_key, language) or ""
        notification_id = str(uuid.uuid4())

        if effective_mode == "template":
            payload = self._builder.build_template(
                notification_id=notification_id,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                client_name=client_name,
                template_name=template_name,
                subject=subject,
                event_type=event_type,
                context_data=context,
                channels=channels,
                language=language,
            )
        else:
            payload = self._builder.build_rendered(
                notification_id=notification_id,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                client_name=client_name,
                html_content=html_content,
                text_content=text_content,
                subject=subject,
                event_type=event_type,
                channels=channels,
                language=language,
            )

        return self._queue.enqueue(self.task_name, payload)

    async def adispatch(
        self,
        *,
        recipient_email: str,
        recipient_phone: str | None = None,
        client_name: str = "",
        template_name: str = "",
        event_type: str,
        channels: list[str],
        language: str = "de",
        subject_key: str,
        mode: str | None = None,
        html_content: str = "",
        text_content: str = "",
        **context: Any,
    ) -> str | None:
        """Async version of dispatch() for ASGI views."""
        effective_mode = mode or self.mode

        subject = self._selector.get(subject_key, language) or ""
        notification_id = str(uuid.uuid4())

        if effective_mode == "template":
            payload = self._builder.build_template(
                notification_id=notification_id,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                client_name=client_name,
                template_name=template_name,
                subject=subject,
                event_type=event_type,
                context_data=context,
                channels=channels,
                language=language,
            )
        else:
            payload = self._builder.build_rendered(
                notification_id=notification_id,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                client_name=client_name,
                html_content=html_content,
                text_content=text_content,
                subject=subject,
                event_type=event_type,
                channels=channels,
                language=language,
            )

        return await self._queue.aenqueue(self.task_name, payload)


def _get_builder() -> NotificationPayloadBuilder:
    from .builder import NotificationPayloadBuilder

    return NotificationPayloadBuilder()
