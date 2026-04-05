from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from django.http import HttpRequest


class NotificationItem(TypedDict):
    label: str
    count: int
    url: str
    icon: str


class NotificationRegistry:
    """Generic topbar notification surface for cabinet features."""

    def __init__(self) -> None:
        self._providers: list[tuple[str, Callable[[Any], NotificationItem | None]]] = []

    def register(
        self, key: str
    ) -> Callable[[Callable[[Any], NotificationItem | None]], Callable[[Any], NotificationItem | None]]:
        def decorator(fn: Callable[[Any], NotificationItem | None]) -> Callable[[Any], NotificationItem | None]:
            self._providers.append((key, fn))
            return fn

        return decorator

    def get_items(self, request: HttpRequest) -> list[NotificationItem]:
        items: list[NotificationItem] = []
        for _key, fn in self._providers:
            item: NotificationItem | None = None
            try:
                item = fn(request or object())
            except Exception:
                item = None
            if item:
                items.append(item)
        return items


notification_registry = NotificationRegistry()
# Deprecated compatibility alias for pre-refactor imports.
bell_registry = notification_registry

__all__ = ["NotificationItem", "NotificationRegistry", "notification_registry", "bell_registry"]
