"""Decorator-based registry for domain notification event handlers."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, cast

from .contracts import NotificationDispatchSpec


class NotificationEventRegistry:
    """Collect handlers that translate domain events into dispatch specs."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[object]] = {}

    def register(self, event_type: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a handler for a logical notification event."""

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._handlers.setdefault(event_type, []).append(fn)
            return fn

        return decorator

    def get_handlers(self, event_type: str) -> list[object]:
        """Return all handlers registered for one logical event type."""
        return list(self._handlers.get(event_type, ()))

    def build_specs(self, event_type: str, *args: Any, **kwargs: Any) -> list[NotificationDispatchSpec]:
        """Execute handlers and normalize their output into dispatch specs."""
        specs: list[NotificationDispatchSpec] = []
        for handler in self.get_handlers(event_type):
            result = cast(Callable[..., Any], handler)(*args, **kwargs)
            if result is None:
                continue
            if isinstance(result, NotificationDispatchSpec):
                specs.append(result)
                continue
            if isinstance(result, Iterable) and not isinstance(result, str | bytes | dict):
                for item in result:
                    if item is None:
                        continue
                    if not isinstance(item, NotificationDispatchSpec):
                        raise TypeError(
                            f"Notification handler for '{event_type}' returned non-spec item: {type(item)!r}"
                        )
                    specs.append(item)
                continue
            raise TypeError(
                f"Notification handler for '{event_type}' must return NotificationDispatchSpec, "
                f"an iterable of specs, or None; got {type(result)!r}"
            )
        return specs


notification_event_registry = NotificationEventRegistry()


def notification_handler(event_type: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Convenience decorator backed by the global notification event registry."""
    return notification_event_registry.register(event_type)


__all__ = ["NotificationEventRegistry", "notification_event_registry", "notification_handler"]
