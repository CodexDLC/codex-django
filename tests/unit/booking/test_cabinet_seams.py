from __future__ import annotations

from datetime import date

import pytest

from codex_django.booking.cabinet import (
    BookingCabinetAvailabilityService,
    BookingCabinetWorkflowBase,
    present_booking_modal_state,
)
from codex_django.booking.contracts import (
    BookingModalActionState,
    BookingModalState,
    BookingProfileState,
    BookingSummaryItemState,
)

pytestmark = pytest.mark.unit


class FakeGateway:
    def get_available_slots(self, *, target_date, **kwargs):
        if target_date == date(2026, 4, 10):
            return {"09:00": True, "10:00": False}
        return []


def test_booking_availability_facade_normalizes_slots_and_days():
    service = BookingCabinetAvailabilityService(FakeGateway())

    assert service.get_slots(booking_date="2026-04-10", service_ids=[1]) == ["09:00"]
    assert service.get_available_dates(start_date=date(2026, 4, 10), horizon=2, service_ids=[1]) == {"2026-04-10"}


def test_booking_workflow_base_builds_generic_selector_payloads():
    workflow = BookingCabinetWorkflowBase()

    selector = workflow.build_service_selector(
        services=[{"id": 7, "name": "Cut", "price": "30", "duration_minutes": 45, "resource_ids": [1, 2]}]
    )

    assert selector.items[0].id == "7"
    assert selector.items[0].title == "Cut"
    assert selector.items[0].master_ids == [1, 2]


def test_booking_modal_presenter_uses_action_url_policy():
    state = BookingModalState(
        booking_id=10,
        title="Booking",
        profile=BookingProfileState(name="Ada"),
        summary_items=[BookingSummaryItemState(label="Time", value="09:00")],
        actions=[BookingModalActionState(label="Confirm", kind="confirm", value="confirm")],
    )

    modal = present_booking_modal_state(
        state,
        action_url_resolver=lambda action, modal_state: f"/booking/{modal_state.booking_id}/{action.value}/",
    )

    assert modal.title == "Booking"
    assert modal.sections[0].type == "profile"
    assert modal.sections[-1].actions[0].url == "/booking/10/confirm/"
