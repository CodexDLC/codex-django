"""Data contracts for dashboard widget payloads.

This module defines the dataclasses that dashboard selectors return and
widget templates consume. Widgets live in
``cabinet/templates/cabinet/widgets/`` and are registered via
:class:`~codex_django.cabinet.types.registry.DashboardWidget`.

The typical data flow is::

    selector function → returns widget payload dataclass
        ↓
    DashboardSelector cache layer
        ↓
    context processor injects into template context
        ↓
    dashboard/index.html renders {% include widget.template %}
        ↓
    widget template reads typed payload from context

Widget types:

- :class:`MetricWidgetData` — single KPI number with optional trend.
- :class:`TableWidgetData` — tabular data with typed column definitions.
- :class:`ListWidgetData` — vertical list of labelled items with optional avatars.

Supporting types:

- :class:`TableColumn` — column descriptor reused by both
  :class:`TableWidgetData` (dashboard) and
  :class:`~codex_django.cabinet.types.components.DataTableData` (page component).
- :class:`ListItem` — single row in a :class:`ListWidgetData`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TableColumn:
    """Descriptor for a single column in a table widget or data table component.

    Shared by :class:`TableWidgetData` (dashboard widget) and
    :class:`~codex_django.cabinet.types.components.DataTableData` (full-page
    component). The template uses ``col.key`` to read the corresponding value
    from each row dict.

    Attributes:
        key: Dict key used to look up the cell value in each row.
            Example: ``"status"`` reads ``row["status"]``.
        label: Column header text shown to the user.
        align: Horizontal text alignment. One of ``"left"``, ``"center"``,
            ``"right"``. Defaults to ``"left"``.
        bold: If ``True``, cell text is rendered in bold. Useful for primary
            identifier columns (e.g. client name). Defaults to ``False``.
        muted: If ``True``, cell text is rendered in muted colour (secondary
            information). Defaults to ``False``.
        sortable: If ``True``, the column header renders a sort toggle.
            Sorting logic must be implemented by the view. Defaults to ``False``.
        badge_key: If set, the cell value is rendered as a coloured badge.
            The value of this attribute is the context key that maps the cell
            value to a Bootstrap colour name (e.g. ``"status_color_map"``).
            Defaults to ``None`` (plain text).
        icon_key: If set, an icon is prepended to the cell value. The value
            is the context key for a Bootstrap Icons class mapping.
            Defaults to ``None``.

    Example::

        TableColumn(key="status", label="Статус", badge_key="status_color_map")
        TableColumn(key="name",   label="Клиент", bold=True)
        TableColumn(key="amount", label="Сумма",  align="right")
    """

    key: str
    label: str
    align: str = "left"
    bold: bool = False
    muted: bool = False
    sortable: bool = False
    badge_key: str | None = None
    icon_key: str | None = None


@dataclass
class ListItem:
    """A single row in a dashboard list widget.

    Used as elements of :attr:`ListWidgetData.items`. Each item displays
    a primary label, a primary value, and optional secondary lines and avatar.

    Attributes:
        label: Primary descriptor on the left side, e.g. client name or
            service title.
        value: Primary metric on the right side, e.g. ``"12 000 ₽"``.
        avatar: Optional URL to an avatar image, or a 1–2 character initials
            string. When set, an avatar circle is rendered before the label.
            Defaults to ``None``.
        sublabel: Optional secondary text below ``label``, rendered smaller
            and muted. Defaults to ``None``.
        subvalue: Optional secondary text below ``value``.
            Defaults to ``None``.

    Example::

        ListItem(label="Иван Петров", value="5 сеансов", avatar="ИП",
                 sublabel="Постоянный клиент")
    """

    label: str
    value: str
    avatar: str | None = None
    sublabel: str | None = None
    subvalue: str | None = None


@dataclass
class MetricWidgetData:
    """Payload for a KPI metric widget (``cabinet/widgets/kpi.html``).

    Displays a single headline number with an optional trend indicator
    (up/down/neutral arrow + label) and a decorative icon.

    Attributes:
        label: Short description of the metric, e.g. ``"Новые клиенты"``.
        value: Formatted metric value, e.g. ``"142"`` or ``"18 500 ₽"``.
        unit: Optional unit suffix displayed after ``value``, e.g. ``"₽"``,
            ``"%"``. Defaults to ``None``.
        trend_value: Formatted change value, e.g. ``"+12%"`` or ``"−3"``.
            Displayed alongside the trend arrow. Defaults to ``None``.
        trend_label: Short context for the trend, e.g. ``"за неделю"``.
            Defaults to ``None``.
        trend_direction: Visual direction of the trend arrow. One of
            ``"up"`` (green), ``"down"`` (red), ``"neutral"`` (grey).
            Defaults to ``"neutral"``.
        icon: Bootstrap Icons class name for the decorative icon,
            e.g. ``"bi-people"``. Defaults to ``None``.

    Example::

        MetricWidgetData(
            label="Новые клиенты",
            value="142",
            trend_value="+12%",
            trend_label="за неделю",
            trend_direction="up",
            icon="bi-people",
        )
    """

    label: str
    value: str
    unit: str | None = None
    trend_value: str | None = None
    trend_label: str | None = None
    trend_direction: str = "neutral"  # "up" | "down" | "neutral"
    icon: str | None = None
    url: str | None = None


@dataclass
class TableWidgetData:
    """Payload for a table dashboard widget (``cabinet/widgets/table.html``).

    Renders a compact data table inside a dashboard card. For a full-page
    sortable/filterable table, use
    :class:`~codex_django.cabinet.types.components.DataTableData` instead.

    Attributes:
        columns: Ordered list of :class:`TableColumn` descriptors that define
            headers and rendering behaviour.
        rows: List of dicts where each key corresponds to a
            :attr:`TableColumn.key`. Extra keys are ignored by the template.

    Example::

        TableWidgetData(
            columns=[
                TableColumn(key="name",   label="Клиент", bold=True),
                TableColumn(key="date",   label="Дата"),
                TableColumn(key="amount", label="Сумма", align="right"),
            ],
            rows=[
                {"name": "Иван П.", "date": "01.04.2026", "amount": "3 500 ₽"},
                {"name": "Анна С.", "date": "31.03.2026", "amount": "1 200 ₽"},
            ],
        )
    """

    columns: list[TableColumn]
    rows: list[dict[str, Any]]


@dataclass
class ListWidgetData:
    """Payload for a list dashboard widget (``cabinet/widgets/list.html``).

    Renders a vertical list of labelled items with optional avatar circles
    inside a dashboard card. For a full-page list, use
    :class:`~codex_django.cabinet.types.components.ListViewData` instead.

    Attributes:
        items: Ordered list of :class:`ListItem` instances.
        title: Optional card title rendered above the list.
            Defaults to ``None`` (no title).

    Example::

        ListWidgetData(
            title="Топ клиенты",
            items=[
                ListItem(label="Иван Петров", value="12 000 ₽", avatar="ИП"),
                ListItem(label="Анна Смирнова", value="8 500 ₽",  avatar="АС"),
            ],
        )
    """

    items: list[ListItem]
    title: str | None = None
    subtitle: str | None = None
    icon: str | None = None
