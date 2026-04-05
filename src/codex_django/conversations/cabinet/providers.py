from __future__ import annotations

from typing import Any

from django.utils.translation import gettext_lazy as _

from .types import InboxNotificationData


def build_inbox_notification_item(
    *, count: int, url: str, label: str | None = None, icon: str = "bi-envelope"
) -> dict[str, Any] | None:
    if not count:
        return None
    data = InboxNotificationData(
        label=label or str(_("New messages")),
        count=count,
        url=url,
        icon=icon,
    )
    return {
        "label": data.label,
        "count": data.count,
        "url": data.url,
        "icon": data.icon,
    }


__all__ = ["build_inbox_notification_item"]
