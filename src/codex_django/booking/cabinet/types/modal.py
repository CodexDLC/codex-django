from __future__ import annotations

from dataclasses import dataclass, field

from codex_django.cabinet.types.modal import ModalSection


@dataclass
class BookingQuickCreateServiceOption:
    value: str
    label: str
    price_label: str = ""
    duration_label: str = ""


@dataclass
class BookingQuickCreateClientOption:
    value: str
    label: str
    subtitle: str = ""
    email: str = ""
    search_text: str = ""


@dataclass
class BookingQuickCreateData:
    resource_label: str
    date_label: str
    time_label: str
    resource_id: str = ""
    booking_date: str = ""
    selected_time: str = ""
    service_options: list[BookingQuickCreateServiceOption] = field(default_factory=list)
    client_options: list[BookingQuickCreateClientOption] = field(default_factory=list)
    selected_service_id: str = ""
    selected_client_id: str = ""
    client_search_query: str = ""
    client_search_min_chars: int = 3
    new_client_first_name: str = ""
    new_client_last_name: str = ""
    new_client_phone: str = ""
    new_client_email: str = ""
    allow_new_client: bool = True


@dataclass
class BookingSlotPickerOption:
    value: str
    label: str
    available: bool = True


@dataclass
class BookingSlotPickerData:
    selected_date: str
    selected_date_label: str
    selected_time: str = ""
    prev_url: str = ""
    next_url: str = ""
    today_url: str = ""
    calendar_url: str = ""
    slots: list[BookingSlotPickerOption] = field(default_factory=list)


@dataclass
class BookingChainPreviewItem:
    title: str
    subtitle: str = ""
    meta: str = ""


@dataclass
class BookingChainPreviewData:
    title: str = "Chain preview"
    items: list[BookingChainPreviewItem] = field(default_factory=list)


@dataclass
class SlotPickerSection(ModalSection):
    data: BookingSlotPickerData = field(default_factory=lambda: BookingSlotPickerData(selected_date="", selected_date_label=""))
    type: str = "slot_picker"


@dataclass
class QuickCreateSection(ModalSection):
    data: BookingQuickCreateData = field(
        default_factory=lambda: BookingQuickCreateData(resource_label="", date_label="", time_label="")
    )
    type: str = "quick_create"


@dataclass
class ChainPreviewSection(ModalSection):
    data: BookingChainPreviewData = field(default_factory=BookingChainPreviewData)
    type: str = "chain_preview"


__all__ = [
    "BookingQuickCreateServiceOption",
    "BookingQuickCreateClientOption",
    "BookingQuickCreateData",
    "BookingSlotPickerOption",
    "BookingSlotPickerData",
    "BookingChainPreviewItem",
    "BookingChainPreviewData",
    "SlotPickerSection",
    "QuickCreateSection",
    "ChainPreviewSection",
]
