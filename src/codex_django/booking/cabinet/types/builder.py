from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceItem:
    id: str
    title: str
    price: str
    duration: int
    category: str = "all"
    description: str = ""
    master_ids: list[int] = field(default_factory=list)
    exclusive_group: str = ""
    conflicts_with: list[str] = field(default_factory=list)
    replacement_mode: str = "replace"


@dataclass
class ServiceSelectorData:
    items: list[ServiceItem]
    categories: list[tuple[str, str]] = field(default_factory=list)
    search_placeholder: str = "Search services..."


@dataclass
class ClientSelectorData:
    clients: list[dict[str, Any]] = field(default_factory=list)
    search_placeholder: str = "Search by name or phone..."


@dataclass
class DateTimePickerData:
    available_days: list[dict[str, Any]]
    time_slots: list[str]
    calendar_cells: list[dict[str, Any]] = field(default_factory=list)
    busy_slots: list[str] = field(default_factory=list)
    current_month: str = ""
    default_date: str = ""
    slot_matrix_json: str = "{}"


@dataclass
class BookingSummaryData:
    confirm_url: str
    reset_url: str = ""
    masters: list[dict[str, Any]] = field(default_factory=list)


__all__ = [
    "ServiceItem",
    "ServiceSelectorData",
    "ClientSelectorData",
    "DateTimePickerData",
    "BookingSummaryData",
]
