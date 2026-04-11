"""Stable runtime contracts for resource-slot booking integrations.

These contracts sit above the booking engine adapter layer and below
project-specific feature scaffolds. Generated booking features import
these types from ``codex_django.booking`` so cabinet integration and
project adapter seams remain stable across projects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Protocol


@dataclass(frozen=True)
class BookingProfileState:
    """Profile header data shown in booking cabinet modals."""

    name: str
    subtitle: str = ""
    avatar: str = ""


@dataclass(frozen=True)
class BookingSummaryItemState:
    """Single key/value row in a booking modal summary block."""

    label: str
    value: str


@dataclass(frozen=True)
class BookingFormFieldState:
    """Declarative form-field state for booking cabinet modals."""

    name: str
    label: str
    field_type: str = "text"
    placeholder: str = ""
    value: str = ""
    options: list[tuple[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class BookingFormState:
    """Form section state for booking cabinet modals."""

    fields: list[BookingFormFieldState] = field(default_factory=list)


@dataclass(frozen=True)
class BookingCalendarPrefillState:
    """Resolved booking context extracted from a calendar slot."""

    resource_id: int | None
    resource_name: str
    booking_date: str
    start_time: str
    slot_duration_minutes: int = 30
    col: int | None = None
    row: int | None = None


@dataclass(frozen=True)
class BookingSlotOptionState:
    """Single selectable slot in a modal slot-picker."""

    value: str
    label: str
    available: bool = True


@dataclass(frozen=True)
class BookingSlotPickerState:
    """Booking-native date navigation and slot selection state."""

    selected_date: str
    selected_date_label: str
    selected_time: str = ""
    prev_url: str = ""
    next_url: str = ""
    today_url: str = ""
    calendar_url: str = ""
    slots: list[BookingSlotOptionState] = field(default_factory=list)


@dataclass(frozen=True)
class BookingQuickCreateServiceOptionState:
    """Available service option for quick-create modals."""

    value: str
    label: str
    price_label: str = ""
    duration_label: str = ""


@dataclass(frozen=True)
class BookingQuickCreateClientOptionState:
    """Available client option for quick-create modals."""

    value: str
    label: str
    subtitle: str = ""
    email: str = ""
    search_text: str = ""


@dataclass(frozen=True)
class BookingQuickCreateState:
    """Quick-create modal state for a single appointment from a calendar slot."""

    prefill: BookingCalendarPrefillState
    service_options: list[BookingQuickCreateServiceOptionState] = field(default_factory=list)
    client_options: list[BookingQuickCreateClientOptionState] = field(default_factory=list)
    selected_service_id: str = ""
    selected_client_id: str = ""
    client_search_query: str = ""
    client_search_min_chars: int = 3
    new_client_first_name: str = ""
    new_client_last_name: str = ""
    new_client_phone: str = ""
    new_client_email: str = ""
    allow_new_client: bool = True


@dataclass(frozen=True)
class BookingChainPreviewItemState:
    """Single row in a booking chain preview block."""

    title: str
    subtitle: str = ""
    meta: str = ""


@dataclass(frozen=True)
class BookingChainPreviewState:
    """Preview of a same-session booking chain."""

    title: str = "Chain preview"
    items: list[BookingChainPreviewItemState] = field(default_factory=list)


@dataclass(frozen=True)
class BookingModalActionState:
    """Action descriptor for booking cabinet modals."""

    label: str
    kind: str
    value: str = ""
    method: str = "GET"
    style: str = "btn-primary"
    icon: str = ""


@dataclass(frozen=True)
class BookingModalState:
    """Canonical state contract for a booking cabinet modal."""

    booking_id: int
    title: str
    mode: str = "detail"
    profile: BookingProfileState | None = None
    summary_items: list[BookingSummaryItemState] = field(default_factory=list)
    form: BookingFormState | None = None
    slot_picker: BookingSlotPickerState | None = None
    quick_create: BookingQuickCreateState | None = None
    chain_preview: BookingChainPreviewState | None = None
    actions: list[BookingModalActionState] = field(default_factory=list)


@dataclass(frozen=True)
class BookingActionResult:
    """Result contract for booking actions initiated from cabinet."""

    ok: bool
    code: str
    message: str
    ui_effect: str
    target_url: str
    field_errors: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class BookingFeatureModels:
    """Concrete project models required by the resource-slot engine gateway."""

    appointment_model: type[Any]
    resource_model: type[Any]
    service_model: type[Any]
    working_day_model: type[Any]
    day_off_model: type[Any]
    booking_settings_model: type[Any]


class BookingBridge(Protocol):
    """Feature-owned adapter that exposes booking state to cabinet."""

    def get_modal_state(self, request: Any, booking_id: int, mode: str) -> BookingModalState: ...

    def execute_action(
        self,
        request: Any,
        booking_id: int,
        action: str,
        payload: dict[str, Any] | Any,
    ) -> BookingActionResult: ...


class BookingProjectDataProvider(Protocol):
    """Project adapter seam for scaffolded resource-slot booking features."""

    def get_feature_models(self) -> BookingFeatureModels: ...

    def get_service_categories(self) -> Any: ...

    def get_cabinet_masters(self) -> list[dict[str, Any]]: ...

    def get_cabinet_clients(self) -> list[dict[str, Any]]: ...

    def get_cabinet_services(self) -> list[dict[str, Any]]: ...

    def get_cabinet_appointments(self) -> list[dict[str, Any]]: ...

    def get_schedule_prefill(self, *, schedule_date: str, col: int, row: int) -> BookingCalendarPrefillState: ...

    def get_quick_create_services(
        self,
        *,
        resource_id: int | None,
        booking_date: str,
        start_time: str,
    ) -> list[BookingQuickCreateServiceOptionState]: ...

    def get_quick_create_clients(self) -> list[BookingQuickCreateClientOptionState]: ...

    def create_quick_client(
        self,
        *,
        first_name: str,
        last_name: str,
        phone: str,
        email: str,
    ) -> dict[str, Any]: ...

    def get_quick_create_slot_options(
        self,
        *,
        resource_id: int,
        booking_date: str,
        service_ids: list[int] | None = None,
    ) -> list[str]: ...

    def create_quick_appointment(
        self,
        *,
        resource_id: int,
        booking_date: str,
        start_time: str,
        service_id: int,
        client_name: str,
        client_phone: str,
        client_email: str = "",
    ) -> dict[str, Any]: ...

    def update_quick_appointment(
        self, *, booking_id: int, booking_date: str, start_time: str
    ) -> dict[str, Any] | None: ...

    def run_cabinet_action(self, *, booking_id: int, action: str, redirect_url: str) -> BookingActionResult: ...


class BookingEngineGateway(Protocol):
    """Feature-facing gateway over the engine adapter and selectors."""

    def get_calendar_data(
        self,
        *,
        year: int,
        month: int,
        today: date | None = None,
        selected_date: date | None = None,
    ) -> list[dict[str, Any]]: ...

    def get_available_slots(self, *, service_ids: list[int], target_date: date, **kwargs: Any) -> Any: ...

    def get_nearest_slots(self, *, service_ids: list[int], search_from: date, **kwargs: Any) -> Any: ...

    def get_resource_day_slots(
        self,
        *,
        resource_id: int,
        target_date: date,
    ) -> list[str]: ...

    def create_booking(
        self,
        *,
        service_ids: list[int],
        target_date: date,
        selected_time: str,
        resource_id: int | None,
        client: Any,
        **kwargs: Any,
    ) -> Any: ...


class BookingWorkflowService(Protocol):
    """Workflow seam used by views and cabinet entrypoints."""

    def get_schedule_context(self, request: Any) -> dict[str, Any]: ...

    def get_new_booking_context(self, request: Any) -> dict[str, Any]: ...

    def get_list_context(self, request: Any, *, status: str | None = None) -> dict[str, Any]: ...
