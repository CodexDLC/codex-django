from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AppointmentAggregateAction:
    label: str
    url: str = ""
    method: str = "GET"
    style: str = "btn-outline-primary"
    icon: str = ""
    scope: str = "group"


@dataclass
class AppointmentAggregateHeader:
    title: str
    subtitle: str = ""
    status: str = ""
    status_tone: str = ""
    timeline_label: str = ""
    total_label: str = ""
    kind: str = "single"


@dataclass
class AppointmentAggregateItem:
    id: str
    title: str
    subtitle: str = ""
    service_label: str = ""
    specialist_label: str = ""
    start_label: str = ""
    end_label: str = ""
    status: str = ""
    status_tone: str = ""
    price_label: str = ""
    meta: list[str] = field(default_factory=list)
    actions: list[AppointmentAggregateAction] = field(default_factory=list)


@dataclass
class AppointmentAggregateData:
    header: AppointmentAggregateHeader
    items: list[AppointmentAggregateItem] = field(default_factory=list)
    actions: list[AppointmentAggregateAction] = field(default_factory=list)
    can_reschedule_group: bool = False
    can_cancel_group: bool = False


__all__ = [
    "AppointmentAggregateAction",
    "AppointmentAggregateHeader",
    "AppointmentAggregateItem",
    "AppointmentAggregateData",
]
