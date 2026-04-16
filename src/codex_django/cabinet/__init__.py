"""Public cabinet integration API."""

from typing import Any

from .notifications import notification_registry
from .presenters import ModalPresenter, present_modal_state
from .quick_access import (
    build_candidate_key,
    get_enabled_staff_quick_access,
    get_staff_quick_access_candidates,
    parse_selected_keys,
)
from .registry import cabinet_registry, configure_space, declare
from .reports import (
    ChartAxisData,
    ChartDatasetData,
    ReportChartData,
    ReportPageData,
    ReportPeriod,
    ReportSummaryCardData,
    ReportTabData,
    ReportTableData,
    resolve_report_period,
)
from .runtime import CabinetRequestContext, CabinetRuntimeResolver, CabinetSpaceConfig
from .types import (
    ActionSection,
    CabinetModuleConfig,
    CabinetSection,
    CalendarGridData,
    CalendarSlot,
    CardGridData,
    CardItem,
    DashboardWidget,
    DataTableData,
    FormField,
    FormSection,
    KeyValueItem,
    ListItem,
    ListRow,
    ListViewData,
    ListWidgetData,
    MetricWidgetData,
    ModalAction,
    ModalContentData,
    ModalSection,
    NavAction,
    ProfileSection,
    Shortcut,
    SidebarItem,
    SplitPanelData,
    SummarySection,
    TableAction,
    TableColumn,
    TableFilter,
    TableWidgetData,
    TopbarEntry,
)

__all__ = [
    "declare",
    "configure_space",
    "cabinet_registry",
    "notification_registry",
    "CabinetModuleMixin",
    "CabinetTemplateView",
    "StaffRequiredMixin",
    "OwnerRequiredMixin",
    "CabinetRuntimeResolver",
    "CabinetRequestContext",
    "CabinetSpaceConfig",
    "ModalPresenter",
    "present_modal_state",
    "build_candidate_key",
    "parse_selected_keys",
    "get_staff_quick_access_candidates",
    "get_enabled_staff_quick_access",
    "ReportPeriod",
    "resolve_report_period",
    "ChartAxisData",
    "ChartDatasetData",
    "ReportChartData",
    "ReportPageData",
    "ReportSummaryCardData",
    "ReportTabData",
    "ReportTableData",
    "TopbarEntry",
    "CabinetModuleConfig",
    "SidebarItem",
    "Shortcut",
    "TableColumn",
    "ListItem",
    "MetricWidgetData",
    "TableWidgetData",
    "ListWidgetData",
    "TableFilter",
    "TableAction",
    "DataTableData",
    "CalendarSlot",
    "CalendarGridData",
    "CardItem",
    "CardGridData",
    "ListRow",
    "ListViewData",
    "SplitPanelData",
    "ModalSection",
    "ProfileSection",
    "KeyValueItem",
    "SummarySection",
    "FormField",
    "FormSection",
    "ModalAction",
    "ActionSection",
    "ModalContentData",
    "CabinetSection",
    "NavAction",
    "DashboardWidget",
]


def __getattr__(name: str) -> Any:
    if name in {"CabinetModuleMixin", "CabinetTemplateView", "StaffRequiredMixin", "OwnerRequiredMixin"}:
        from . import mixins

        return getattr(mixins, name)
    raise AttributeError(f"module 'codex_django.cabinet' has no attribute {name!r}")
