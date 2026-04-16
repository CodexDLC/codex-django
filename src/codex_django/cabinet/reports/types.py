"""Typed contracts for data-driven cabinet report pages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from codex_django.cabinet.types import TableColumn

ChartType = Literal["line", "bar", "doughnut", "pie"]
AxisPosition = Literal["left", "right", "top", "bottom"]


@dataclass
class ReportTabData:
    """A selectable report tab."""

    key: str
    label: str
    icon: str | None = None


@dataclass
class ReportSummaryCardData:
    """Small summary metric shown inside a report page."""

    label: str
    value: str
    hint: str | None = None
    trend_value: str | None = None
    trend_direction: str = "neutral"
    icon: str | None = None


@dataclass
class ChartAxisData:
    """Chart.js scale descriptor for report charts."""

    id: str
    position: AxisPosition = "left"
    label: str | None = None
    begin_at_zero: bool = True
    draw_on_chart_area: bool = True
    tick_prefix: str = ""
    tick_suffix: str = ""

    def as_chartjs(self) -> dict[str, Any]:
        """Return a Chart.js-compatible scale object."""

        axis: dict[str, Any] = {
            "type": "linear",
            "display": True,
            "position": self.position,
            "beginAtZero": self.begin_at_zero,
            "grid": {"drawOnChartArea": self.draw_on_chart_area},
        }
        if self.label:
            axis["title"] = {"display": True, "text": self.label}
        if self.tick_prefix or self.tick_suffix:
            axis["ticks"] = {"prefix": self.tick_prefix, "suffix": self.tick_suffix}
        return axis


@dataclass
class ChartDatasetData:
    """Chart.js dataset descriptor used by report charts."""

    label: str
    data: list[int | float | None]
    type: ChartType | None = None
    y_axis_id: str | None = None
    border_color: str | None = None
    background_color: str | None = None
    fill: bool | None = None
    tension: float | None = None
    border_width: float | None = None
    point_radius: float | None = None
    border_dash: list[int] | None = None
    border_radius: int | None = None

    def as_chartjs(self) -> dict[str, Any]:
        """Return a Chart.js-compatible dataset object."""

        payload: dict[str, Any] = {"label": self.label, "data": self.data}
        optional = {
            "type": self.type,
            "yAxisID": self.y_axis_id,
            "borderColor": self.border_color,
            "backgroundColor": self.background_color,
            "fill": self.fill,
            "tension": self.tension,
            "borderWidth": self.border_width,
            "pointRadius": self.point_radius,
            "borderDash": self.border_dash,
            "borderRadius": self.border_radius,
        }
        payload.update({key: value for key, value in optional.items() if value is not None})
        return payload


@dataclass
class ReportChartData:
    """Main chart payload for a report section."""

    chart_id: str
    title: str
    labels: list[str]
    datasets: list[ChartDatasetData | dict[str, Any]]
    type: ChartType = "line"
    description: str | None = None
    icon: str | None = None
    axes: list[ChartAxisData] = field(default_factory=list)
    height: str = "300px"
    show_legend: bool = True

    def as_widget_config(self) -> dict[str, Any]:
        """Return a config object consumed by ``chartWidget``."""

        config: dict[str, Any] = {
            "chart_id": self.chart_id,
            "title": self.title,
            "type": self.type,
            "chart_labels": self.labels,
            "datasets": [
                dataset.as_chartjs() if isinstance(dataset, ChartDatasetData) else dataset for dataset in self.datasets
            ],
            "height": self.height,
            "show_legend": self.show_legend,
        }
        if self.description:
            config["subtitle"] = self.description
        if self.icon:
            config["icon"] = self.icon
        if self.axes:
            config["scales"] = {axis.id: axis.as_chartjs() for axis in self.axes}
        return config


@dataclass
class ReportTableData:
    """Dense report table with optional summary row."""

    columns: list[TableColumn | dict[str, Any]]
    rows: list[dict[str, Any]]
    title: str = "Data Breakdown"
    subtitle: str | None = None
    summary_row: dict[str, Any] = field(default_factory=dict)
    primary_summary: str | None = None
    secondary_summary: str | None = None
    empty_message: str = "No data available for the selected period."


@dataclass
class ReportPageData:
    """Complete data contract for a reusable cabinet report page."""

    title: str
    summary: str
    active_tab: str
    active_period: str
    tabs: list[ReportTabData | dict[str, Any]]
    period_options: list[ReportTabData | dict[str, Any]]
    period_label: str
    table: ReportTableData
    chart: ReportChartData | None = None
    summary_cards: list[ReportSummaryCardData | dict[str, Any]] = field(default_factory=list)
    export_url: str | None = None
