"""Generic modal-state presenter for cabinet components."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from codex_django.cabinet.types.modal import (
    ActionSection,
    FormField,
    FormSection,
    KeyValueItem,
    ModalAction,
    ModalContentData,
    ModalSection,
    ProfileSection,
    SummarySection,
)

ActionUrlResolver = Callable[[Any], str]


class ModalPresenter:
    """Map generic domain state into ``ModalContentData``."""

    def __init__(self, action_url_resolver: ActionUrlResolver | None = None) -> None:
        self.action_url_resolver = action_url_resolver

    def present(self, state: Any) -> ModalContentData:
        sections: list[ModalSection] = []

        profile = _get(state, "profile")
        if profile:
            sections.append(
                ProfileSection(
                    name=str(_get(profile, "name", "")),
                    subtitle=str(_get(profile, "subtitle", "")),
                    avatar=str(_get(profile, "avatar", "")),
                )
            )

        summary_items = list(_iter(_get(state, "summary_items", [])))
        if summary_items:
            sections.append(
                SummarySection(
                    items=[
                        KeyValueItem(label=str(_get(item, "label", "")), value=str(_get(item, "value", "")))
                        for item in summary_items
                    ]
                )
            )

        form = _get(state, "form")
        fields = list(_iter(_get(form, "fields", []))) if form else []
        if fields:
            sections.append(
                FormSection(
                    fields=[
                        FormField(
                            name=str(_get(field, "name", "")),
                            label=str(_get(field, "label", "")),
                            field_type=str(_get(field, "field_type", "text")),
                            placeholder=str(_get(field, "placeholder", "")),
                            value=str(_get(field, "value", "")),
                            options=list(_iter(_get(field, "options", []))),
                        )
                        for field in fields
                    ]
                )
            )

        actions = list(_iter(_get(state, "actions", [])))
        if actions:
            sections.append(ActionSection(actions=[self._present_action(action) for action in actions]))

        return ModalContentData(title=str(_get(state, "title", "")), sections=sections)

    def _present_action(self, action: Any) -> ModalAction:
        kind = str(_get(action, "kind", "")).lower()
        method = str(_get(action, "method", "GET")).upper()
        if kind == "close":
            method = "CLOSE"
        url = self.action_url_resolver(action) if self.action_url_resolver else str(_get(action, "url", ""))
        return ModalAction(
            label=str(_get(action, "label", "")),
            url=url,
            method=method,
            style=str(_get(action, "style", "btn-primary")),
            icon=str(_get(action, "icon", "")),
        )


def present_modal_state(state: Any, action_url_resolver: ActionUrlResolver | None = None) -> ModalContentData:
    """Present a generic modal state object as cabinet modal content."""
    return ModalPresenter(action_url_resolver=action_url_resolver).present(state)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _iter(value: object) -> Iterable[Any]:
    if value is None:
        return ()
    if isinstance(value, str | bytes):
        return ()
    if isinstance(value, Iterable):
        return value
    return ()
