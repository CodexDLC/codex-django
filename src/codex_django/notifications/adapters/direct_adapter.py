"""
DjangoDirectAdapter
===================
Inline (no-worker) notification delivery via Django's send_mail().

Useful for:
- Development environments without Redis/ARQ
- Simple use cases where async delivery is not required
- Fallback when the queue is unavailable

Supports both payload modes:
- Mode 1 (template): requires a TemplateRenderer from codex_platform.
  Renders Jinja2 identically to the production worker — dev == prod.
- Mode 2 (rendered): sends html_content directly without rendering.

Usage::

    # Mode 2 only (no renderer needed):
    adapter = DjangoDirectAdapter()

    # Mode 1 + Mode 2:
    from codex_platform.notifications.renderer import TemplateRenderer
    renderer = TemplateRenderer(templates_dir="path/to/templates")
    adapter = DjangoDirectAdapter(renderer=renderer)

    # Works the same as DjangoQueueAdapter:
    adapter.enqueue("send_notification_task", payload=data)
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)


class DjangoDirectAdapter:
    """Deliver notifications inline via Django ``send_mail()``.

    Notes:
        The adapter implements the same enqueue interface as the queue-based
        adapter, which makes it useful for development, testing, and fallback
        delivery paths.
    """

    def __init__(
        self,
        renderer: Any = None,
        use_on_commit: bool = True,
    ) -> None:
        self._renderer = renderer
        self._use_on_commit = use_on_commit

    def enqueue(self, task_name: str, payload: dict[str, Any]) -> str | None:
        """Synchronously deliver or schedule delivery of a notification payload."""
        if self._use_on_commit:
            from django.db import transaction

            transaction.on_commit(lambda: self._send(payload))
            return None
        return self._send(payload)

    async def aenqueue(self, task_name: str, payload: dict[str, Any]) -> str | None:
        """Asynchronously deliver a notification payload in a worker thread."""
        import asyncio

        await asyncio.to_thread(self._send, payload)
        return None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _send(self, payload: dict[str, Any]) -> str | None:
        """Send a rendered notification payload through Django mail."""
        mode = payload.get("mode", "rendered")

        if mode == "template":
            html_content, text_content = self._render(payload)
        else:
            html_content = payload.get("html_content", "")
            text_content = payload.get("text_content", "")

        recipient = payload.get("recipient_email", "")
        subject = payload.get("subject", "")

        if not recipient:
            log.warning("DjangoDirectAdapter: recipient_email is empty, skipping send")
            return None

        from django.conf import settings
        from django.core.mail import send_mail

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

        send_mail(
            subject=subject,
            message=text_content,
            from_email=from_email,
            recipient_list=[recipient],
            html_message=html_content or None,
            fail_silently=False,
        )
        log.info("DjangoDirectAdapter: sent email to %s (subject=%r)", recipient, subject)
        return None

    def _render(self, payload: dict[str, Any]) -> tuple[str, str]:
        """Render a template-mode payload using the configured renderer."""
        if self._renderer is None:
            raise ValueError(
                "DjangoDirectAdapter: 'renderer' is required for Mode 1 payloads "
                "(mode='template'). Pass a TemplateRenderer instance or use Mode 2 "
                "(build_rendered) to avoid rendering."
            )
        template_name: str = payload["template_name"]
        context_data: dict[str, Any] = payload.get("context_data", {})
        html_content: str = self._renderer.render(template_name, context_data)
        text_content: str = payload.get("text_content", "")
        return html_content, text_content
