"""Generic booking availability facade for cabinet workflows."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta
from typing import Any

from codex_django.booking.contracts import BookingEngineGateway
from codex_django.booking.selectors import (
    build_picker_day_rows,
    normalize_slot_payload,
    parse_resource_selections,
)


class BookingCabinetAvailabilityService:
    """Normalize gateway availability calls for cabinet date/slot widgets."""

    def __init__(self, gateway: BookingEngineGateway | None = None) -> None:
        self.gateway = gateway

    def get_available_dates(
        self,
        *,
        start_date: date,
        horizon: int,
        service_ids: Iterable[int] | None = None,
        locked_resource_id: int | None = None,
        resource_selections: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> set[str]:
        """Return ISO dates that have at least one available slot."""
        service_id_list = [int(value) for value in service_ids or []]
        if self.gateway is None or not service_id_list or horizon <= 0:
            return set()

        available: set[str] = set()
        for offset in range(horizon):
            current_date = start_date + timedelta(days=offset)
            slots = self.get_slots(
                booking_date=current_date,
                service_ids=service_id_list,
                locked_resource_id=locked_resource_id,
                resource_selections=resource_selections,
                **kwargs,
            )
            if slots:
                available.add(current_date.isoformat())
        return available

    def build_day_rows(
        self,
        *,
        start_date: date,
        horizon: int,
        service_ids: Iterable[int] | None = None,
        locked_resource_id: int | None = None,
        resource_selections: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> list[dict[str, str | int | bool]]:
        """Build the standard cabinet date-picker day payload."""
        service_id_list = [int(value) for value in service_ids or []]
        available_dates = self.get_available_dates(
            start_date=start_date,
            horizon=horizon,
            service_ids=service_id_list,
            locked_resource_id=locked_resource_id,
            resource_selections=resource_selections,
            **kwargs,
        )
        return build_picker_day_rows(
            start_date=start_date,
            horizon=horizon,
            available_dates=available_dates,
            has_service_scope=bool(service_id_list),
        )

    def get_slots(
        self,
        *,
        booking_date: date | str,
        service_ids: Iterable[int] | None = None,
        locked_resource_id: int | None = None,
        resource_selections: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> list[str]:
        """Return normalized available start times for a date."""
        if self.gateway is None:
            return []
        service_id_list = [int(value) for value in service_ids or []]
        if not service_id_list:
            return []

        target_date = date.fromisoformat(booking_date) if isinstance(booking_date, str) else booking_date
        payload = self.gateway.get_available_slots(
            service_ids=service_id_list,
            target_date=target_date,
            locked_resource_id=locked_resource_id,
            resource_selections=resource_selections,
            **kwargs,
        )
        return normalize_slot_payload(payload)


__all__ = ["BookingCabinetAvailabilityService", "parse_resource_selections"]
