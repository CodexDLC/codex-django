"""Present booking cabinet states as generic cabinet modal content."""

from __future__ import annotations

from collections.abc import Callable

from codex_django.booking.cabinet.types import (
    BookingChainPreviewData,
    BookingChainPreviewItem,
    BookingQuickCreateClientOption,
    BookingQuickCreateData,
    BookingQuickCreateServiceOption,
    BookingSlotPickerData,
    BookingSlotPickerOption,
    ChainPreviewSection,
    QuickCreateSection,
    SlotPickerSection,
)
from codex_django.booking.contracts import BookingModalActionState, BookingModalState
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

BookingActionUrlResolver = Callable[[BookingModalActionState, BookingModalState], str]


class BookingModalPresenter:
    """Map ``BookingModalState`` to reusable cabinet modal sections."""

    def __init__(self, action_url_resolver: BookingActionUrlResolver | None = None) -> None:
        self.action_url_resolver = action_url_resolver

    def present(self, state: BookingModalState) -> ModalContentData:
        sections: list[ModalSection] = []

        if state.profile:
            sections.append(
                ProfileSection(
                    name=state.profile.name,
                    subtitle=state.profile.subtitle,
                    avatar=state.profile.avatar,
                )
            )

        if state.summary_items:
            sections.append(
                SummarySection(items=[KeyValueItem(label=item.label, value=item.value) for item in state.summary_items])
            )

        if state.form and state.form.fields:
            sections.append(
                FormSection(
                    fields=[
                        FormField(
                            name=field.name,
                            label=field.label,
                            field_type=field.field_type,
                            placeholder=field.placeholder,
                            value=field.value,
                            options=list(field.options),
                        )
                        for field in state.form.fields
                    ]
                )
            )

        if state.slot_picker:
            sections.append(
                SlotPickerSection(
                    data=BookingSlotPickerData(
                        selected_date=state.slot_picker.selected_date,
                        selected_date_label=state.slot_picker.selected_date_label,
                        selected_time=state.slot_picker.selected_time,
                        prev_url=state.slot_picker.prev_url,
                        next_url=state.slot_picker.next_url,
                        today_url=state.slot_picker.today_url,
                        calendar_url=state.slot_picker.calendar_url,
                        slots=[
                            BookingSlotPickerOption(value=slot.value, label=slot.label, available=slot.available)
                            for slot in state.slot_picker.slots
                        ],
                    )
                )
            )

        if state.quick_create:
            prefill = state.quick_create.prefill
            sections.append(
                QuickCreateSection(
                    data=BookingQuickCreateData(
                        resource_label=prefill.resource_name,
                        date_label=prefill.booking_date,
                        time_label=prefill.start_time,
                        resource_id=str(prefill.resource_id or ""),
                        booking_date=prefill.booking_date,
                        selected_time=prefill.start_time,
                        service_options=[
                            BookingQuickCreateServiceOption(
                                value=option.value,
                                label=option.label,
                                price_label=option.price_label,
                                duration_label=option.duration_label,
                            )
                            for option in state.quick_create.service_options
                        ],
                        client_options=[
                            BookingQuickCreateClientOption(
                                value=option.value,
                                label=option.label,
                                subtitle=option.subtitle,
                                email=option.email,
                                search_text=option.search_text,
                            )
                            for option in state.quick_create.client_options
                        ],
                        selected_service_id=state.quick_create.selected_service_id,
                        selected_client_id=state.quick_create.selected_client_id,
                        client_search_query=state.quick_create.client_search_query,
                        client_search_min_chars=state.quick_create.client_search_min_chars,
                        new_client_first_name=state.quick_create.new_client_first_name,
                        new_client_last_name=state.quick_create.new_client_last_name,
                        new_client_phone=state.quick_create.new_client_phone,
                        new_client_email=state.quick_create.new_client_email,
                        allow_new_client=state.quick_create.allow_new_client,
                    )
                )
            )

        if state.chain_preview:
            sections.append(
                ChainPreviewSection(
                    data=BookingChainPreviewData(
                        title=state.chain_preview.title,
                        items=[
                            BookingChainPreviewItem(title=item.title, subtitle=item.subtitle, meta=item.meta)
                            for item in state.chain_preview.items
                        ],
                    )
                )
            )

        if state.actions:
            sections.append(ActionSection(actions=[self._present_action(action, state) for action in state.actions]))

        return ModalContentData(title=state.title, sections=sections)

    def _present_action(self, action: BookingModalActionState, state: BookingModalState) -> ModalAction:
        method = action.method.upper()
        if action.kind.lower() == "close":
            method = "CLOSE"
        url = self.action_url_resolver(action, state) if self.action_url_resolver else action.value
        return ModalAction(
            label=action.label,
            url=url,
            method=method,
            style=action.style,
            icon=action.icon,
        )


def present_booking_modal_state(
    state: BookingModalState,
    action_url_resolver: BookingActionUrlResolver | None = None,
) -> ModalContentData:
    """Present booking modal state using the reusable cabinet modal contract."""
    return BookingModalPresenter(action_url_resolver=action_url_resolver).present(state)


__all__ = ["BookingActionUrlResolver", "BookingModalPresenter", "present_booking_modal_state"]
