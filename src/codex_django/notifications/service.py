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
        default_language = "de"  # override per project if needed

        def send_booking_confirmed(self, booking):
            self.dispatch(
                recipient_email=booking.client_email,
                template_name="emails/booking_confirmed.html",
                event_type="booking_confirmed",
                channels=["email"],
                subject_key="booking_confirmed_subject",
                booking=booking,
            )
"""

from __future__ import annotations

import uuid
from typing import Any

from .builder import NotificationPayloadBuilder
from .contracts import NotificationDispatchSpec, QueueAdapterProtocol
from .registry import notification_event_registry


class BaseNotificationEngine:
    """Coordinate subject lookup, payload building, and queue dispatch.

    Notes:
        ``task_name`` identifies the worker task that performs delivery.
        ``mode`` controls whether the worker renders a template or receives
        pre-rendered content directly.
    """

    task_name: str = "send_universal_notification_task"
    mode: str = "template"  # default mode for all dispatch() calls
    default_language: str = "de"

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
        language: str = "",
        subject_key: str,
        subject: str = "",
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
                Falls back to ``default_language`` when empty.
            subject_key: Content key used to resolve the localized subject.
            subject: Optional explicit subject override. When provided, the
                selector lookup is skipped.
            mode: Optional per-call override for ``template`` or ``rendered`` mode.
            html_content: Pre-rendered HTML body for ``rendered`` mode.
            text_content: Optional plain-text fallback for ``rendered`` mode.
            **context: Extra payload context passed to the worker.

        Returns:
            Queue job ID when the adapter returns one, otherwise ``None``.
        """
        effective_mode = mode or self.mode
        lang = language or self.default_language

        resolved_subject = subject or self._selector.get(subject_key, lang) or ""
        notification_id = str(uuid.uuid4())

        if effective_mode == "template":
            payload = self._builder.build_template(
                notification_id=notification_id,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                client_name=client_name,
                template_name=template_name,
                subject=resolved_subject,
                event_type=event_type,
                context_data=context,
                channels=channels,
                language=lang,
            )
        else:
            payload = self._builder.build_rendered(
                notification_id=notification_id,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                client_name=client_name,
                html_content=html_content,
                text_content=text_content,
                subject=resolved_subject,
                event_type=event_type,
                channels=channels,
                language=lang,
                context_data=context,
            )

        return self._queue.enqueue(self.task_name, payload)

    def dispatch_spec(self, spec: NotificationDispatchSpec) -> str | None:
        """Dispatch one prebuilt spec produced by a domain handler."""
        return self.dispatch(
            recipient_email=spec.recipient_email,
            recipient_phone=spec.recipient_phone,
            client_name=spec.client_name,
            template_name=spec.template_name,
            event_type=spec.event_type,
            channels=spec.channels,
            language=spec.language,
            subject_key=spec.subject_key,
            subject=spec.subject,
            mode=spec.mode,
            html_content=spec.html_content,
            text_content=spec.text_content,
            **spec.context,
        )

    def dispatch_event(self, event_type: str, *args: Any, **kwargs: Any) -> list[str | None]:
        """Resolve registered handlers for an event and dispatch every resulting spec."""
        specs = notification_event_registry.build_specs(event_type, *args, **kwargs)
        return [self.dispatch_spec(spec) for spec in specs]

    async def adispatch(
        self,
        *,
        recipient_email: str,
        recipient_phone: str | None = None,
        client_name: str = "",
        template_name: str = "",
        event_type: str,
        channels: list[str],
        language: str = "",
        subject_key: str,
        subject: str = "",
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
                Falls back to ``default_language`` when empty.
            subject_key: Content key used to resolve the localized subject.
            subject: Optional explicit subject override. When provided, the
                selector lookup is skipped.
            mode: Optional per-call override for ``template`` or ``rendered`` mode.
            html_content: Pre-rendered HTML body for ``rendered`` mode.
            text_content: Optional plain-text fallback for ``rendered`` mode.
            **context: Extra payload context passed to the worker.

        Returns:
            Queue job ID when the adapter returns one, otherwise ``None``.
        """
        effective_mode = mode or self.mode
        lang = language or self.default_language

        resolved_subject = subject or self._selector.get(subject_key, lang) or ""
        notification_id = str(uuid.uuid4())

        if effective_mode == "template":
            payload = self._builder.build_template(
                notification_id=notification_id,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                client_name=client_name,
                template_name=template_name,
                subject=resolved_subject,
                event_type=event_type,
                context_data=context,
                channels=channels,
                language=lang,
            )
        else:
            payload = self._builder.build_rendered(
                notification_id=notification_id,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                client_name=client_name,
                html_content=html_content,
                text_content=text_content,
                subject=resolved_subject,
                event_type=event_type,
                channels=channels,
                language=lang,
                context_data=context,
            )

        return await self._queue.aenqueue(self.task_name, payload)

    async def adispatch_spec(self, spec: NotificationDispatchSpec) -> str | None:
        """Async counterpart to :meth:`dispatch_spec`."""
        return await self.adispatch(
            recipient_email=spec.recipient_email,
            recipient_phone=spec.recipient_phone,
            client_name=spec.client_name,
            template_name=spec.template_name,
            event_type=spec.event_type,
            channels=spec.channels,
            language=spec.language,
            subject_key=spec.subject_key,
            subject=spec.subject,
            mode=spec.mode,
            html_content=spec.html_content,
            text_content=spec.text_content,
            **spec.context,
        )

    async def adispatch_event(self, event_type: str, *args: Any, **kwargs: Any) -> list[str | None]:
        """Async counterpart to :meth:`dispatch_event`."""
        specs = notification_event_registry.build_specs(event_type, *args, **kwargs)
        results: list[str | None] = []
        for spec in specs:
            results.append(await self.adispatch_spec(spec))
        return results


def _get_builder() -> NotificationPayloadBuilder:
    """Return the payload builder used by the notification engine."""
    from .builder import NotificationPayloadBuilder

    return NotificationPayloadBuilder()
