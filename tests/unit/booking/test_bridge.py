from __future__ import annotations

import pytest

from codex_django.booking.cabinet.bridge import BookingBridge
from codex_django.booking.contracts import BookingBridge as ContractsBookingBridge


@pytest.mark.unit
def test_booking_cabinet_bridge_reexports_contract_bridge():
    assert BookingBridge is ContractsBookingBridge
