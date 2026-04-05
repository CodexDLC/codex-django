"""Unit tests for stable booking contracts."""

from __future__ import annotations

import pytest

from codex_django.booking import (
    BookingActionResult,
    BookingCalendarPrefillState,
    BookingFeatureModels,
    BookingModalState,
    BookingProfileState,
    BookingQuickCreateState,
    BookingSlotOptionState,
    BookingSlotPickerState,
)

pytestmark = pytest.mark.unit


def test_contracts_are_importable_from_public_booking_module():
    state = BookingModalState(
        booking_id=101,
        title="Booking #101",
        profile=BookingProfileState(name="Ada"),
    )
    result = BookingActionResult(
        ok=True,
        code="booking-confirm",
        message="ok",
        ui_effect="reload_modal",
        target_url="/cabinet/booking/101/modal/",
    )

    assert state.profile is not None
    assert state.profile.name == "Ada"
    assert result.target_url.endswith("/modal/")


def test_feature_models_bundle_keeps_runtime_model_references():
    bundle = BookingFeatureModels(
        appointment_model=object,
        master_model=dict,
        service_model=list,
        working_day_model=tuple,
        day_off_model=set,
        booking_settings_model=str,
        site_settings_model=int,
    )

    assert bundle.appointment_model is object
    assert bundle.site_settings_model is int


def test_booking_modal_state_supports_quick_create_and_slot_picker_sections():
    state = BookingModalState(
        booking_id=0,
        title="Create",
        quick_create=BookingQuickCreateState(
            prefill=BookingCalendarPrefillState(
                resource_id=1,
                resource_name="Alexander Petrov",
                booking_date="2026-03-23",
                start_time="09:00",
            )
        ),
        slot_picker=BookingSlotPickerState(
            selected_date="2026-03-24",
            selected_date_label="Mar 24, 2026",
            selected_time="10:30",
            slots=[BookingSlotOptionState(value="10:30", label="10:30")],
        ),
    )

    assert state.quick_create is not None
    assert state.quick_create.prefill.resource_name == "Alexander Petrov"
    assert state.slot_picker is not None
    assert state.slot_picker.slots[0].value == "10:30"
