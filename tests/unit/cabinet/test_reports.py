"""Unit tests for reusable cabinet report contracts."""

from __future__ import annotations

from datetime import date

import pytest
from django.template.loader import render_to_string

from codex_django.cabinet import (
    ChartAxisData,
    ChartDatasetData,
    ReportChartData,
    ReportPageData,
    ReportSummaryCardData,
    ReportTabData,
    ReportTableData,
    TableColumn,
    resolve_report_period,
)

pytestmark = pytest.mark.unit


def test_resolve_report_period_defaults_to_month_with_previous_window():
    period = resolve_report_period("unknown", today=date(2026, 4, 16))

    assert period.key == "month"
    assert period.date_from == date(2026, 4, 1)
    assert period.date_to == date(2026, 4, 16)
    assert period.previous_from == date(2026, 3, 16)
    assert period.previous_to == date(2026, 3, 31)
    assert period.days == 16


def test_resolve_report_period_supports_calendar_quarter():
    period = resolve_report_period("quarter", today=date(2026, 5, 9))

    assert period.key == "quarter"
    assert period.date_from == date(2026, 4, 1)
    assert period.date_to == date(2026, 5, 9)
    assert period.previous_from == date(2026, 2, 21)
    assert period.previous_to == date(2026, 3, 31)


def test_report_chart_config_exports_mixed_dual_axis_payload():
    chart = ReportChartData(
        chart_id="revenueVolumeChart",
        title="Revenue",
        labels=["01.04", "02.04"],
        type="bar",
        datasets=[
            ChartDatasetData(
                label="Orders",
                data=[2, 3],
                type="bar",
                y_axis_id="y",
                background_color="rgba(15,23,42,0.15)",
            ),
            ChartDatasetData(
                label="Revenue",
                data=[1200.0, 1500.0],
                type="line",
                y_axis_id="y1",
                border_color="#2563eb",
                fill=False,
            ),
        ],
        axes=[
            ChartAxisData(id="y", position="left", label="Orders"),
            ChartAxisData(id="y1", position="right", label="Revenue", draw_on_chart_area=False, tick_prefix="$"),
        ],
    )

    config = chart.as_widget_config()

    assert config["type"] == "bar"
    assert config["datasets"][0]["type"] == "bar"
    assert config["datasets"][1]["type"] == "line"
    assert config["datasets"][1]["yAxisID"] == "y1"
    assert config["scales"]["y1"]["position"] == "right"
    assert config["scales"]["y1"]["ticks"]["prefix"] == "$"


def test_report_partials_render_data_driven_contract():
    report = ReportPageData(
        title="Reports",
        summary="Revenue, order volume, and average check.",
        active_tab="revenue",
        active_period="month",
        tabs=[ReportTabData(key="revenue", label="Revenue", icon="bi-currency-dollar")],
        period_options=[ReportTabData(key="month", label="Month")],
        period_label="Selected period: 01.04.2026 - 16.04.2026",
        summary_cards=[
            ReportSummaryCardData(label="Revenue", value="$2,700.00", hint="Gross sales", icon="bi-cash")
        ],
        table=ReportTableData(
            title="Data Breakdown",
            columns=[
                TableColumn(key="label", label="Day", bold=True),
                TableColumn(key="revenue", label="Revenue", align="right"),
            ],
            rows=[{"label": "01.04", "revenue": "$1,200.00"}],
            summary_row={"label": "Total", "revenue": "$1,200.00"},
        ),
        chart=ReportChartData(
            chart_id="revenueChart",
            title="Revenue Trend",
            labels=["01.04"],
            datasets=[ChartDatasetData(label="Revenue", data=[1200.0])],
        ),
    )

    table_html = render_to_string("cabinet/reports/table.html", {"table": report.table})
    chart_html = render_to_string("cabinet/reports/chart.html", {"chart": report.chart})
    html = table_html + chart_html

    assert "cab-report-table__grid" in html
    assert "Revenue Trend" in html
    assert "revenueChart" in html
