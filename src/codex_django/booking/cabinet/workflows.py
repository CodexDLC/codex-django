from __future__ import annotations

from datetime import date
from typing import Any

from codex_django.booking.contracts import BookingProjectDataProvider, BookingWorkflowService

from .availability import BookingCabinetAvailabilityService
from .types import (
    BookingSummaryData,
    ClientSelectorData,
    DateTimePickerData,
    ServiceItem,
    ServiceSelectorData,
)


class BookingCabinetWorkflowBase:
    """Generic payload assembly helpers for cabinet booking views."""

    def __init__(
        self,
        *,
        provider: BookingProjectDataProvider | None = None,
        availability: BookingCabinetAvailabilityService | None = None,
    ) -> None:
        self.provider = provider
        self.availability = availability or BookingCabinetAvailabilityService()

    def build_service_selector(
        self,
        services: list[dict[str, Any]] | None = None,
        *,
        categories: list[tuple[str, str]] | None = None,
        search_placeholder: str = "Search services...",
    ) -> ServiceSelectorData:
        """Build the standard service selector payload."""
        raw_services = services
        if raw_services is None and self.provider is not None:
            raw_services = self.provider.get_cabinet_services()

        return ServiceSelectorData(
            items=[self._service_item(service) for service in raw_services or []],
            categories=categories or [],
            search_placeholder=search_placeholder,
        )

    def build_client_selector(
        self,
        clients: list[dict[str, Any]] | None = None,
        *,
        search_placeholder: str = "Search by name or phone...",
    ) -> ClientSelectorData:
        """Build the standard client selector payload."""
        if clients is None and self.provider is not None:
            clients = self.provider.get_cabinet_clients()
        return ClientSelectorData(clients=clients or [], search_placeholder=search_placeholder)

    def build_date_time_picker(
        self,
        *,
        start_date: date,
        horizon: int,
        service_ids: list[int] | None = None,
        locked_resource_id: int | None = None,
        resource_selections: dict[str, str] | None = None,
        selected_date: date | str | None = None,
        time_slots: list[str] | None = None,
    ) -> DateTimePickerData:
        """Build the standard cabinet date/time picker payload."""
        service_id_list = service_ids or []
        days = self.availability.build_day_rows(
            start_date=start_date,
            horizon=horizon,
            service_ids=service_id_list,
            locked_resource_id=locked_resource_id,
            resource_selections=resource_selections,
        )

        default_date = selected_date.isoformat() if isinstance(selected_date, date) else str(selected_date or "")
        if time_slots is None and default_date:
            time_slots = self.availability.get_slots(
                booking_date=default_date,
                service_ids=service_id_list,
                locked_resource_id=locked_resource_id,
                resource_selections=resource_selections,
            )

        return DateTimePickerData(
            available_days=days,
            time_slots=time_slots or [],
            default_date=default_date,
            current_month=start_date.strftime("%B %Y"),
        )

    def build_summary(
        self,
        *,
        confirm_url: str,
        reset_url: str = "",
        resources: list[dict[str, Any]] | None = None,
    ) -> BookingSummaryData:
        """Build the standard booking summary payload."""
        if resources is None and self.provider is not None:
            resources = self.provider.get_cabinet_masters()
        return BookingSummaryData(confirm_url=confirm_url, reset_url=reset_url, masters=resources or [])

    def build_list_context(self, request: Any, *, status: str | None = None) -> dict[str, Any]:
        """Build a minimal generic list context from the project provider."""
        appointments = self.provider.get_cabinet_appointments() if self.provider is not None else []
        if status:
            appointments = [item for item in appointments if str(item.get("status", "")) == status]
        return {"appointments": appointments, "status": status, "request": request}

    @staticmethod
    def _service_item(service: dict[str, Any]) -> ServiceItem:
        return ServiceItem(
            id=str(service.get("id", "")),
            title=str(service.get("title") or service.get("name") or ""),
            price=str(service.get("price", "")),
            duration=int(service.get("duration") or service.get("duration_minutes") or 0),
            category=str(service.get("category", "all")),
            description=str(service.get("description", "")),
            master_ids=[int(value) for value in (service.get("master_ids") or service.get("resource_ids") or [])],
            exclusive_group=str(service.get("exclusive_group", "")),
            conflicts_with=[str(value) for value in service.get("conflicts_with", [])],
            replacement_mode=str(service.get("replacement_mode", "replace")),
        )


__all__ = ["BookingWorkflowService", "BookingCabinetWorkflowBase"]
