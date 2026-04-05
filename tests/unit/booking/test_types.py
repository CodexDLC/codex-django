import pytest
from codex_django.booking.cabinet.types.aggregate import (
    AppointmentAggregateAction, 
    AppointmentAggregateHeader, 
    AppointmentAggregateItem, 
    AppointmentAggregateData
)
from codex_django.booking.cabinet.types.appointment import AppointmentDisplayData
from codex_django.booking.cabinet.types.modal import (
    BookingQuickCreateData,
    BookingSlotPickerData,
    BookingSlotPickerOption,
    BookingChainPreviewData
)

@pytest.mark.unit
def test_appointment_aggregate_types():
    header = AppointmentAggregateHeader(title="Test Header")
    action = AppointmentAggregateAction(label="Edit", url="/edit/")
    item = AppointmentAggregateItem(id="1", title="App 1")
    data = AppointmentAggregateData(header=header, items=[item], actions=[action])
    assert data.header.title == "Test Header"
    assert len(data.items) == 1

@pytest.mark.unit
def test_appointment_display_data():
    d = AppointmentDisplayData(id="1", title="App 1")
    assert d.id == "1"

@pytest.mark.unit
def test_booking_modal_types():
    q = BookingQuickCreateData(resource_label="R", date_label="D", time_label="T")
    assert q.resource_label == "R"
    
    s = BookingSlotPickerData(selected_date="2024-01-01", selected_date_label="Jan 1")
    assert s.selected_date == "2024-01-01"
    
    o = BookingSlotPickerOption(value="10:00", label="10:00")
    assert o.value == "10:00"
    
    p = BookingChainPreviewData(title="Chain")
    assert p.title == "Chain"
