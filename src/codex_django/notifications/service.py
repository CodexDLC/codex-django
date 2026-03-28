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
    """Minimal queue adapter contract required by the notification engine."""

    def enqueue(self, task_name: str, payload: dict[str, Any]) -> str | None: ...
    async def aenqueue(self, task_name: str, payload: dict[str, Any]) -> str | None: ...


class BaseNotificationEngine:
    """Coordinate subject lookup, payload building, and queue dispatch.

    Notes:
        ``task_name`` identifies the worker task that performs delivery.
        ``mode`` controls whether the worker renders a template or receives
        pre-rendered content directly.
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
        """Initialize the engine with project-provided infrastructure adapters.

        Args:
            queue_adapter: Adapter responsible for queueing or delivering work.
            cache_adapter: Cache adapter used by the project selector layer.
            i18n_adapter: Adapter that manages temporary language overrides.
            selector: Content selector used to resolve localized subjects.
        """
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
        """Resolve content metadata, build a payload, and enqueue a notification.

        Args:
            recipient_email: Destination email address.
            recipient_phone: Optional phone number for SMS/WhatsApp channels.
            client_name: Optional human-readable recipient name.
            template_name: Worker-side template path for ``template`` mode.
            event_type: Logical notification event identifier.
            channels: Delivery channels to request from the worker.
            language: Language code used for subject lookup and payload metadata.
            subject_key: Content key used to resolve the localized subject.
            mode: Optional per-call override for ``template`` or ``rendered`` mode.
            html_content: Pre-rendered HTML body for ``rendered`` mode.
            text_content: Optional plain-text fallback for ``rendered`` mode.
            **context: Extra payload context passed to the worker.

        Returns:
            Queue job ID when the adapter returns one, otherwise ``None``.
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
        """Asynchronous counterpart to :meth:`dispatch` for async call sites.

        Args:
            recipient_email: Destination email address.
            recipient_phone: Optional phone number for SMS/WhatsApp channels.
            client_name: Optional human-readable recipient name.
            template_name: Worker-side template path for ``template`` mode.
            event_type: Logical notification event identifier.
            channels: Delivery channels to request from the worker.
            language: Language code used for subject lookup and payload metadata.
            subject_key: Content key used to resolve the localized subject.
            mode: Optional per-call override for ``template`` or ``rendered`` mode.
            html_content: Pre-rendered HTML body for ``rendered`` mode.
            text_content: Optional plain-text fallback for ``rendered`` mode.
            **context: Extra payload context passed to the worker.

        Returns:
            Queue job ID when the adapter returns one, otherwise ``None``.
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

        return await self._queue.aenqueue(self.task_name, payload)


def _get_builder() -> NotificationPayloadBuilder:
    """Return the payload builder used by the notification engine."""
    from .builder import NotificationPayloadBuilder

    return NotificationPayloadBuilder()
