"""Navigation helpers for project-owned messaging cabinet registration."""

from __future__ import annotations

from codex_django.cabinet import SidebarItem, TopbarEntry


def build_messaging_sidebar(
    *,
    mailbox_url: str,
    campaigns_url: str,
    recipients_url: str,
    delivery_log_url: str,
    unread_badge_key: str = "unread_messages_count",
) -> list[SidebarItem]:
    """Return the default Messaging sidebar without registering it globally."""
    return [
        SidebarItem(label="Mailbox", url=mailbox_url, icon="bi-inbox", badge_key=unread_badge_key, order=10),
        SidebarItem(label="Campaigns", url=campaigns_url, icon="bi-megaphone", order=20),
        SidebarItem(label="Recipients", url=recipients_url, icon="bi-people", order=30),
        SidebarItem(label="Delivery log", url=delivery_log_url, icon="bi-list-check", order=40),
    ]


def build_messaging_topbar(
    url: str,
    *,
    label: str = "Messaging",
    group: str = "services",
    order: int = 20,
) -> TopbarEntry:
    """Return the default Messaging topbar entry without registering it globally."""
    return TopbarEntry(group=group, label=label, icon="bi-envelope-paper", url=url, order=order)


__all__ = ["build_messaging_sidebar", "build_messaging_topbar"]
