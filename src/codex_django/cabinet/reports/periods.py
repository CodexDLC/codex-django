"""Date-window helpers for reusable cabinet reports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

ReportPeriodKey = Literal["week", "month", "quarter"]


@dataclass(frozen=True)
class ReportPeriod:
    """Resolved report period with a matching previous comparison window."""

    key: ReportPeriodKey
    date_from: date
    date_to: date
    previous_from: date
    previous_to: date

    @property
    def days(self) -> int:
        """Return the inclusive number of days in the current period."""

        return (self.date_to - self.date_from).days + 1


def _period_bounds(period: str | None, today: date) -> tuple[ReportPeriodKey, date, date]:
    key: ReportPeriodKey
    if period == "week":
        key = "week"
        return key, today - timedelta(days=6), today
    if period == "quarter":
        key = "quarter"
        quarter_start_month = ((today.month - 1) // 3) * 3 + 1
        return key, date(today.year, quarter_start_month, 1), today
    key = "month"
    return key, today.replace(day=1), today


def resolve_report_period(period: str | None = None, *, today: date | None = None) -> ReportPeriod:
    """Resolve a named report period and its previous comparison period.

    Args:
        period: ``"week"``, ``"month"``, or ``"quarter"``. Unknown values
            fall back to ``"month"``.
        today: Optional anchor date for deterministic tests.

    Returns:
        A :class:`ReportPeriod` with current and previous inclusive bounds.
    """

    anchor = today or date.today()
    key, date_from, date_to = _period_bounds(period, anchor)
    span_days = (date_to - date_from).days + 1
    previous_to = date_from - timedelta(days=1)
    previous_from = previous_to - timedelta(days=span_days - 1)
    return ReportPeriod(
        key=key,
        date_from=date_from,
        date_to=date_to,
        previous_from=previous_from,
        previous_to=previous_to,
    )
