"""Decorator-based registry for domain messaging event handlers."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, cast

from .contracts import NotificationDispatchSpec


class MessagingEventRegistry:
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

    def email_template(
        self, event_type: str, *, channels: list[str]
    ) -> Callable[[Callable[..., dict[str, Any]]], Callable[..., NotificationDispatchSpec]]:
        """Register a template-mode builder."""

        def decorator(fn: Callable[..., dict[str, Any]]) -> Callable[..., NotificationDispatchSpec]:
            self._validate_registration(event_type, fn, mode="template")

            def builder(*args: Any, **kwargs: Any) -> NotificationDispatchSpec:
                data = self._validate_payload(event_type, fn(*args, **kwargs), mode="template")
                return NotificationDispatchSpec(
                    recipient_email=str(data["recipient_email"]),
                    subject_key=str(data["subject_key"]),
                    event_type=event_type,
                    channels=list(channels),
                    subject=str(data.get("subject", "")),
                    recipient_phone=data.get("recipient_phone"),
                    client_name=str(data.get("client_name", "")),
                    template_name=str(data["template_name"]),
                    language=str(data.get("language", "")),
                    mode="template",
                    context=dict(data.get("context", {})),
                )

            self.register(event_type)(builder)
            return builder

        return decorator

    def email_rendered(
        self, event_type: str, *, channels: list[str]
    ) -> Callable[[Callable[..., dict[str, Any]]], Callable[..., NotificationDispatchSpec]]:
        """Register a rendered-mode builder."""

        def decorator(fn: Callable[..., dict[str, Any]]) -> Callable[..., NotificationDispatchSpec]:
            self._validate_registration(event_type, fn, mode="rendered")

            def builder(*args: Any, **kwargs: Any) -> NotificationDispatchSpec:
                data = self._validate_payload(event_type, fn(*args, **kwargs), mode="rendered")
                return NotificationDispatchSpec(
                    recipient_email=str(data["recipient_email"]),
                    subject_key=str(data["subject_key"]),
                    event_type=event_type,
                    channels=list(channels),
                    subject=str(data.get("subject", "")),
                    recipient_phone=data.get("recipient_phone"),
                    client_name=str(data.get("client_name", "")),
                    language=str(data.get("language", "")),
                    mode="rendered",
                    html_content=str(data["html_content"]),
                    text_content=str(data.get("text_content", "")),
                    context=dict(data.get("context", {})),
                )

            self.register(event_type)(builder)
            return builder

        return decorator

    def _validate_registration(self, event_type: str, fn: Callable[..., dict[str, Any]], *, mode: str) -> None:
        try:
            sample = fn()
        except TypeError:
            return
        self._validate_payload(event_type, sample, mode=mode)

    def _validate_payload(self, event_type: str, data: dict[str, Any], *, mode: str) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise TypeError(f"Handler for '{event_type}' must return dict, got {type(data)!r}")

        required = {"recipient_email", "subject_key"}
        if mode == "template":
            required.add("template_name")
            forbidden = {"html_content", "text_content", "mode"}
        else:
            required.add("html_content")
            forbidden = {"template_name", "mode"}

        missing = sorted(key for key in required if key not in data)
        if missing:
            raise TypeError(f"Handler for '{event_type}' is missing required keys: {', '.join(missing)}")

        present_forbidden = sorted(key for key in forbidden if key in data)
        if present_forbidden:
            raise TypeError(f"Handler for '{event_type}' returned forbidden keys: {', '.join(present_forbidden)}")

        return data


messaging_event_registry = MessagingEventRegistry()


def notification_handler(event_type: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Convenience decorator backed by the global messaging event registry."""
    return messaging_event_registry.register(event_type)


def email_template(
    event_type: str, *, channels: list[str] | None = None
) -> Callable[[Callable[..., dict[str, Any]]], Callable[..., NotificationDispatchSpec]]:
    """Register a template-mode event builder."""
    return messaging_event_registry.email_template(event_type, channels=list(channels or ["email"]))


def email_rendered(
    event_type: str, *, channels: list[str] | None = None
) -> Callable[[Callable[..., dict[str, Any]]], Callable[..., NotificationDispatchSpec]]:
    """Register a rendered-mode event builder."""
    return messaging_event_registry.email_rendered(event_type, channels=list(channels or ["email"]))


__all__ = [
    "MessagingEventRegistry",
    "email_rendered",
    "email_template",
    "messaging_event_registry",
    "notification_handler",
]
