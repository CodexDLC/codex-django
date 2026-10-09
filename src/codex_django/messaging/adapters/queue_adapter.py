"""
DjangoQueueAdapter
==================
NotificationAdapter implementation that enqueues tasks via DjangoArqClient.

Wraps enqueue() in transaction.on_commit() by default so the ARQ job is
only dispatched after the DB transaction commits successfully.

Usage::

    adapter = DjangoQueueAdapter(arq_client=DjangoArqClient())

    # From a sync view (WSGI):
    adapter.enqueue("send_notification_task", payload=data)

    # From an async view (ASGI):
    await adapter.aenqueue("send_notification_task", payload=data)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .arq_client import DjangoArqClient


class DjangoQueueAdapter:
    """Queue-backed notification adapter for ARQ-based delivery."""

    def __init__(self, arq_client: DjangoArqClient, use_on_commit: bool = True) -> None:
        self._arq = arq_client
        self._use_on_commit = use_on_commit

    def enqueue(self, task_name: str, payload: dict[str, Any]) -> str | None:
        """Synchronously enqueue a notification payload.

        Returns ``None`` when ``use_on_commit=True`` because the job is not
        enqueued until the transaction commits. Otherwise returns the ARQ job id.
        """
        if self._use_on_commit:
            from django.db import transaction

            transaction.on_commit(lambda: self._arq.enqueue(task_name, payload=payload))
            return None
        return self._arq.enqueue(task_name, payload=payload)

    async def aenqueue(self, task_name: str, payload: dict[str, Any]) -> str | None:
        """Asynchronously enqueue a notification payload without ``on_commit``."""
        return await self._arq.aenqueue(task_name, payload=payload)
