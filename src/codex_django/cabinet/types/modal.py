from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ModalSection:
    type: str = "base"


@dataclass
class ProfileSection(ModalSection):
    name: str = ""
    subtitle: str = ""
    avatar: str = ""
    type: str = "profile"


@dataclass
class KeyValueItem:
    label: str
    value: str


@dataclass
class SummarySection(ModalSection):
    items: list[KeyValueItem] = field(default_factory=list)
    type: str = "summary"


@dataclass
class FormField:
    name: str
    label: str
    field_type: str = "text"
    placeholder: str = ""
    value: str = ""
    options: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class FormSection(ModalSection):
    fields: list[FormField] = field(default_factory=list)
    type: str = "form"


@dataclass
class ModalAction:
    label: str
    url: str = ""
    method: str = "GET"
    style: str = "btn-primary"
    icon: str = ""


@dataclass
class ActionSection(ModalSection):
    actions: list[ModalAction] = field(default_factory=list)
    type: str = "actions"


@dataclass
class ModalContentData:
    title: str
    sections: list[ModalSection] = field(default_factory=list)
