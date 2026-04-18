"""Date-window helpers for reusable cabinet reports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Literal

ReportPeriodKey = Literal["week", "month", "quarter", "year", "custom"]


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


def _coerce_date(value: date | str | None) -> date | None:
    if value is None or isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _custom_bounds(
    date_from: date | str | None,
    date_to: date | str | None,
    today: date,
) -> tuple[date, date] | None:
    start = _coerce_date(date_from)
    end = _coerce_date(date_to)
    if start is None or end is None or start > end:
        return None
    return start, end


def _period_bounds(
    period: str | None,
    today: date,
    date_from: date | str | None,
    date_to: date | str | None,
) -> tuple[ReportPeriodKey, date, date]:
    key: ReportPeriodKey
    if period == "week":
        key = "week"
        return key, today - timedelta(days=6), today
    if period == "quarter":
        key = "quarter"
        quarter_start_month = ((today.month - 1) // 3) * 3 + 1
        return key, date(today.year, quarter_start_month, 1), today
    if period == "year":
        key = "year"
        return key, date(today.year, 1, 1), today
    if period == "custom":
        bounds = _custom_bounds(date_from, date_to, today)
        if bounds is not None:
            return "custom", bounds[0], bounds[1]
    key = "month"
    return key, today.replace(day=1), today


def resolve_report_period(
    period: str | None = None,
    *,
    date_from: date | str | None = None,
    date_to: date | str | None = None,
    today: date | None = None,
) -> ReportPeriod:
    """Resolve a named report period and its previous comparison period.

    Args:
        period: One of ``"week"``, ``"month"``, ``"quarter"``, ``"year"``, or
            ``"custom"``. Unknown values (or ``"custom"`` with invalid bounds)
            fall back to ``"month"``.
        date_from: Start of a custom range. Ignored unless ``period`` is
            ``"custom"``. Accepts ``date`` or ISO ``YYYY-MM-DD`` string.
        date_to: End of a custom range. Same rules as ``date_from``.
        today: Optional anchor date for deterministic tests.

    Returns:
        A :class:`ReportPeriod` with current and previous inclusive bounds.
    """

    anchor = today or date.today()
    key, start, end = _period_bounds(period, anchor, date_from, date_to)
    span_days = (end - start).days + 1
    previous_to = start - timedelta(days=1)
    previous_from = previous_to - timedelta(days=span_days - 1)
    return ReportPeriod(
        key=key,
        date_from=start,
        date_to=end,
        previous_from=previous_from,
        previous_to=previous_to,
    )
