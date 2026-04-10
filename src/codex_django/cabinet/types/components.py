"""Data contracts for cabinet content-component templates.

Each dataclass in this module defines the payload that a template in
``cabinet/templates/cabinet/components/`` expects to receive via Django's
``{% include ... with obj=obj %}`` tag.

Design principles:

- **Backend computes, template renders.** All positioning, counts, and
  formatting are calculated by the view or selector before the template
  sees them. Templates contain no business logic.
- **One contract per component.** Each ``include`` receives exactly one
  typed object. The template variable name matches the parameter name
  documented in each class.
- **Alpine.js for client-side state only.** Toggle states (grid/list view,
  search filter) live in ``x-data`` inside the template. No custom JS files.
- **HTMX for server interactions.** Detail panels, modals, and actions
  use ``hx-get`` / ``hx-post``. URLs are passed through the contract.
- **Modal dispatch pattern.** Components do *not* embed modals. They
  dispatch ``$dispatch('open-modal', {url: '...'})`` and the page-level
  ``_modal_base.html`` handles loading.

Available components:

- :class:`DataTableData` → ``components/data_table.html``
- :class:`CalendarGridData` + :class:`CalendarSlot` → ``components/calendar_grid.html``
- :class:`CardGridData` + :class:`CardItem` → ``components/card_grid.html``
- :class:`ListViewData` + :class:`ListRow` → ``components/list_view.html``
- :class:`SplitPanelData` + :class:`ListRow` → ``components/split_panel.html``
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .widgets import TableColumn

# ---------------------------------------------------------------------------
# Data Table
# ---------------------------------------------------------------------------


@dataclass
class TableFilter:
    """A single filter tab or button for :class:`DataTableData`.

    Filter buttons are rendered as a row of toggle buttons above the table.
    Clicking a filter sets ``activeFilter`` in Alpine state; the table
    rows whose ``status`` field matches ``value`` remain visible.

    Attributes:
        key: Machine-readable identifier for the filter, e.g. ``"active"``.
        label: Human-readable button label, e.g. ``"Активные"``.
        value: The value to compare against the row's status field.
            Empty string (default) acts as "show all".

    Example::

        TableFilter(key="pending", label="Ожидают", value="pending")
    """

    key: str
    label: str
    value: str = ""


@dataclass
class TableAction:
    """A row-level action link in a data table or list component.

    Each action renders as a button or link in the last column of the table
    (or in the row's action area). The URL for the action is read from the
    row dict using ``url_key`` as the lookup key.

    Attributes:
        label: Button label text, e.g. ``"Открыть"``, ``"Удалить"``.
        url_key: Key in the row dict whose value is used as the action URL.
            Example: if ``url_key="detail_url"`` and the row is
            ``{"id": 1, "detail_url": "/booking/1/"}``, the action links
            to ``/booking/1/``.
        icon: Bootstrap Icons class name, e.g. ``"bi-eye"``.
            Empty string renders a text-only button.
        style: Visual style. One of:

            - ``"link"`` — plain text link with HTMX modal open (default).
            - ``"btn-primary"`` — Bootstrap primary button.
            - ``"btn-danger"`` — Bootstrap danger button.

    Example::

        TableAction(label="Открыть", url_key="detail_url", icon="bi-eye")
        TableAction(label="Удалить", url_key="delete_url", icon="bi-trash",
                    style="btn-danger")
    """

    label: str
    url_key: str
    icon: str = ""
    style: str = "link"  # "link" | "btn-primary" | "btn-danger"


@dataclass
class DataTableData:
    """Payload contract for ``components/data_table.html``.

    Renders a searchable, filterable data table. Search and filter state
    is managed client-side by Alpine.js (no page reload). Row actions open
    detail modals via HTMX dispatch.

    Template variable: ``table``::

        {% include "cabinet/components/data_table.html" with table=table %}

    Attributes:
        columns: Ordered list of :class:`TableColumn` descriptors. Each
            column defines a header label and how to render cell values.
        rows: List of dicts. Each dict must contain keys matching
            :attr:`~TableColumn.key` for every column.
        filters: Optional list of :class:`TableFilter` instances rendered
            as toggle buttons above the table. Defaults to empty list
            (no filter bar).
        actions: Optional list of :class:`TableAction` instances rendered
            in the last column. Defaults to empty list (no action column).
        search_placeholder: Placeholder text for the search input.
            Empty string (default) hides the search bar entirely.
        empty_message: Message shown when ``rows`` is empty or all rows
            are filtered out. Defaults to ``"Нет данных"``.

    Example::

        from codex_django.cabinet import DataTableData, TableColumn, TableFilter, TableAction

        table = DataTableData(
            columns=[
                TableColumn(key="name",   label="Клиент", bold=True),
                TableColumn(key="date",   label="Дата"),
                TableColumn(key="status", label="Статус", badge_key="status_colors"),
            ],
            rows=list(Appointment.objects.values("name", "date", "status", "detail_url")),
            filters=[
                TableFilter(key="pending",   label="Ожидают",    value="pending"),
                TableFilter(key="confirmed", label="Подтверждены", value="confirmed"),
            ],
            actions=[TableAction(label="Открыть", url_key="detail_url", icon="bi-eye")],
            search_placeholder="Поиск клиентов...",
        )
        return render(request, "booking/appointments.html", {"table": table})
    """

    columns: list[TableColumn]
    rows: list[dict[str, Any]]
    filters: list[TableFilter] = field(default_factory=list)
    actions: list[TableAction] = field(default_factory=list)
    search_placeholder: str = ""
    empty_message: str = "Нет данных"


# ---------------------------------------------------------------------------
# Calendar Grid
# ---------------------------------------------------------------------------


@dataclass
class CalendarSlot:
    """A single event positioned on a :class:`CalendarGridData` grid.

    The grid uses CSS ``grid-column`` and ``grid-row`` to place events.
    All positional values are **zero-based indexes** into
    :attr:`CalendarGridData.cols` and :attr:`CalendarGridData.rows`.
    The backend computes these values; the template only renders them.

    Attributes:
        col: Zero-based column index. Corresponds to the master, room, or
            day at that position in :attr:`CalendarGridData.cols`.
        row: Zero-based row index. Corresponds to the time slot at that
            position in :attr:`CalendarGridData.rows`.
        span: Number of consecutive rows the event occupies. Compute as::

                span = duration_minutes // slot_size_minutes

            For a 1-hour appointment with 30-minute slots: ``60 // 30 = 2``.
        title: Primary event text (e.g. client name or appointment type).
        subtitle: Optional secondary text (e.g. service name).
            Defaults to empty string.
        color: CSS color value or Bootstrap ``bg-*`` class, e.g.
            ``"#6366f1"`` or ``"bg-primary"``. Defaults to
            ``var(--cab-primary)`` if empty.
        url: HTMX endpoint to load when the event is clicked. Opens the
            detail/edit form in ``_modal_base.html``.
            Defaults to empty string (non-clickable).

    Example::

        # 60-minute appointment starting at 9:00 with 30-min slots (row index 2)
        CalendarSlot(
            col=0,           # first master
            row=2,           # 9:00 slot (rows: ["8:00","8:30","9:00",...])
            span=2,          # 60 min / 30 min = 2
            title="Иван П.",
            subtitle="Стрижка",
            color="#6366f1",
            url="/booking/42/",
        )
    """

    col: int
    row: int
    span: int
    title: str
    subtitle: str = ""
    color: str = ""
    badge: str = ""
    badge_style: str = ""
    price: str = ""
    # Content details (e.g. list of tags or objects)
    details: list[dict[str, str]] = field(default_factory=list)
    note: str = ""
    # Icons/indicators (e.g. ["bi-chat", "bi-person-vcard"])
    indicators: list[str] = field(default_factory=list)
    url: str = ""
    left_border: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class CalendarGridData:
    """Payload contract for ``components/calendar_grid.html``.

    Renders a CSS Grid-based scheduling calendar. Columns represent any
    grouping axis (masters, rooms, weekdays), rows represent time slots at
    any granularity. The same contract is shared by two templates:

    - ``calendar_grid.html`` — vertical grid (cols × rows).
    - ``calendar_timeline.html`` — horizontal timeline (future).

    The backend computes all event positions. The template renders a
    background grid of clickable empty slots and overlays events on top.

    Template variable: ``calendar``::

        {% include "cabinet/components/calendar_grid.html" with calendar=calendar %}
        {% include "cabinet/includes/_modal_base.html" %}

    Attributes:
        cols: Column header labels. Can be master names, room names,
            weekday names, or any list of strings.
            Example: ``["Мастер 1", "Мастер 2", "Переговорная A"]``.
        rows: Time slot labels in display order.
            Example: ``["8:00", "8:30", "9:00", ..., "20:00"]``.
        events: List of :class:`CalendarSlot` instances to render.
        slot_height_px: Height of each time slot row in pixels.
            Adjust for denser or sparser grids. Defaults to ``40``.
        new_event_url: HTMX base URL for creating a new event.
            When set, each empty slot becomes clickable and sends
            ``GET {new_event_url}?col=N&row=N``. The response is loaded
            into ``_modal_base.html``. Defaults to empty string (read-only).

    Example::

        from codex_django.cabinet import CalendarGridData, CalendarSlot

        # Build 30-min slots from 8:00 to 20:00
        rows = [f"{h}:{m:02d}" for h in range(8, 20) for m in (0, 30)]

        calendar = CalendarGridData(
            cols=["Мастер 1", "Мастер 2", "Мастер 3"],
            rows=rows,
            events=[
                CalendarSlot(col=0, row=2, span=2,
                             title="Иван П.", subtitle="Стрижка",
                             color="#6366f1", url="/booking/42/"),
            ],
            slot_height_px=40,
            new_event_url="/booking/new/",
        )
        return render(request, "booking/schedule.html", {"calendar": calendar})
    """

    cols: list[str | dict[str, Any]]
    rows: list[str]
    events: list[CalendarSlot]
    slot_height_px: int = 40
    new_event_url: str = ""
    title: str = ""
    current_date: Any = None
    prev_url: str = ""
    next_url: str = ""
    today_url: str = ""
    slot_height: str = "44px"
    time_col_width: str = "60px"
    col_width: str = "1fr"


# ---------------------------------------------------------------------------
# Card Grid
# ---------------------------------------------------------------------------


@dataclass
class CardItem:
    """A single card in a :class:`CardGridData` collection.

    Renders as a card tile in grid mode or as a list row in list mode.
    The ``meta`` field carries icon+text pairs for secondary information
    (e.g. phone number, appointment count, last visit date).

    Attributes:
        id: Unique string identifier used as an HTML key. Should be the
            primary key of the underlying model, e.g. ``str(client.pk)``.
        title: Primary card heading (e.g. client full name).
        subtitle: Optional secondary line below the title
            (e.g. client category or role). Defaults to empty string.
        avatar: URL to an avatar image, or 1–2 character initials string
            for the avatar circle. Defaults to empty string (no avatar).
        badge: Short status label rendered as a badge, e.g. ``"VIP"``,
            ``"Новый"``. Defaults to empty string (no badge).
        badge_style: Bootstrap colour name for the badge background,
            e.g. ``"primary"``, ``"success"``, ``"secondary"``.
            Defaults to ``"secondary"``.
        url: Link target for the card. Can be a detail page URL or an
            HTMX endpoint. Defaults to empty string (non-clickable).
        meta: List of ``(icon, text)`` tuples for secondary information.
            Each tuple renders an icon + label pair.
            Example: ``[("bi-telephone", "+7 999 123-45-67"), ("bi-calendar", "12 визитов")]``.

    Example::

        CardItem(
            id=str(client.pk),
            title=client.full_name,
            subtitle=client.category,
            avatar=client.initials,
            badge="VIP",
            badge_style="warning",
            url=f"/cabinet/clients/{client.pk}/",
            meta=[
                ("bi-telephone", client.phone),
                ("bi-calendar",  f"{client.visit_count} визитов"),
            ],
        )
    """

    id: str
    title: str
    subtitle: str = ""
    avatar: str = ""
    badge: str = ""
    badge_style: str = "secondary"
    url: str = ""
    meta: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class CardGridData:
    """Payload contract for ``components/card_grid.html``.

    Renders a collection of :class:`CardItem` instances either as a
    Bootstrap grid of cards or as a compact list. The user can toggle
    between modes client-side via Alpine.js (no page reload).

    Template variable: ``cards``::

        {% include "cabinet/components/card_grid.html" with cards=cards %}

    Attributes:
        items: List of :class:`CardItem` instances to render.
        view_mode: Initial render mode. ``"grid"`` shows Bootstrap column
            cards; ``"list"`` shows compact rows. Alpine.js manages the
            current mode after the initial render.
            Defaults to ``"grid"``.
        search_placeholder: Placeholder text for the client-side search
            input. Alpine.js filters cards by ``title`` as the user types.
            Empty string (default) hides the search bar.
        empty_message: Message shown when ``items`` is empty.
            Defaults to ``"Нет элементов"``.

    Example::

        from codex_django.cabinet import CardGridData, CardItem

        cards = CardGridData(
            items=[
                CardItem(
                    id=str(c.pk),
                    title=c.full_name,
                    avatar=c.initials,
                    url=f"/cabinet/clients/{c.pk}/",
                )
                for c in Client.objects.all()
            ],
            search_placeholder="Поиск клиентов...",
        )
        return render(request, "clients/index.html", {"cards": cards})
    """

    items: list[CardItem]
    view_mode: str = "grid"  # "grid" | "list"
    search_placeholder: str = ""
    empty_message: str = "Нет элементов"


# ---------------------------------------------------------------------------
# List View
# ---------------------------------------------------------------------------


@dataclass
class ListRow:
    """A single row in a :class:`ListViewData` or :class:`SplitPanelData`.

    Displays a primary label, optional secondary text, and optional meta
    information. Rows can be clickable (HTMX detail load or plain link)
    and carry per-row action buttons.

    Attributes:
        id: Unique string identifier (typically the model's primary key).
        primary: Main row text, e.g. subject line or client name.
        secondary: Optional secondary text rendered smaller below
            ``primary``. Defaults to empty string.
        meta: Optional short metadata shown on the right (e.g. date,
            count). Defaults to empty string.
        avatar: URL or initials string for the avatar circle.
            Defaults to empty string (no avatar).
        url: HTMX endpoint or plain link URL. In :class:`ListViewData`,
            clicking the row dispatches ``open-modal``. In
            :class:`SplitPanelData`, it loads the detail panel.
            Defaults to empty string (non-clickable).
        actions: Per-row :class:`TableAction` list. Rendered as hidden
            buttons that appear on hover. Defaults to empty list.

    Example::

        ListRow(
            id=str(msg.pk),
            primary=msg.subject,
            secondary=msg.sender,
            meta=msg.created_at.strftime("%d.%m"),
            url=f"/cabinet/conversations/{msg.pk}/",
        )
    """

    id: str
    primary: str
    secondary: str = ""
    meta: str = ""
    avatar: str = ""
    url: str = ""
    actions: list[TableAction] = field(default_factory=list)


@dataclass
class ListViewData:
    """Payload contract for ``components/list_view.html``.

    Renders a vertical list of :class:`ListRow` instances with an optional
    search bar. Clicking a row either opens a modal (HTMX) or navigates
    to the row's URL. Row-level action buttons appear on hover.

    Template variable: ``list``::

        {% include "cabinet/components/list_view.html" with list=list_data %}
        {% include "cabinet/includes/_modal_base.html" %}

    Attributes:
        rows: Ordered list of :class:`ListRow` instances.
        search_placeholder: Placeholder text for the Alpine.js search
            input. Filters rows by ``primary`` text as the user types.
            Empty string (default) hides the search bar.
        empty_message: Message shown when ``rows`` is empty.
            Defaults to ``"Нет данных"``.

    Example::

        from codex_django.cabinet import ListViewData, ListRow

        list_data = ListViewData(
            rows=[
                ListRow(
                    id=str(n.pk),
                    primary=n.subject,
                    secondary=n.channel,
                    meta=n.sent_at.strftime("%d.%m %H:%M"),
                    url=f"/cabinet/notifications/{n.pk}/",
                )
                for n in Notification.objects.order_by("-sent_at")
            ],
            search_placeholder="Поиск уведомлений...",
        )
        return render(request, "notifications/log.html", {"list": list_data})
    """

    rows: list[ListRow]
    search_placeholder: str = ""
    empty_message: str = "Нет данных"


# ---------------------------------------------------------------------------
# Split Panel
# ---------------------------------------------------------------------------


@dataclass
class SplitPanelData:
    """Payload contract for ``components/split_panel.html``.

    Renders a two-column layout: a scrollable item list on the left and a
    detail area on the right. Clicking a list item loads its detail via
    HTMX into ``#split-panel-detail`` without a full page reload.

    On mobile (< 768 px) the panels stack vertically.

    Template variable: ``panel``::

        {% include "cabinet/components/split_panel.html" with panel=panel %}

    Note:
        Place ``{% include "cabinet/includes/_modal_base.html" %}`` on the
        page if the detail area opens sub-modals.

    Attributes:
        items: List of :class:`ListRow` instances for the left panel.
        active_id: ``id`` of the initially selected item. The corresponding
            list row gets the ``cab-split-panel__item--active`` CSS class.
            If set, the initial view should also render the detail content
            via ``{% block panel_detail %}`` in the extending template.
            Defaults to empty string (no initial selection).
        detail_url: HTMX base URL for loading item details. The component
            appends ``/<item.id>`` and uses ``hx-get`` to load the right
            panel. Example: ``"/cabinet/conversations"`` → loads
            ``/cabinet/conversations/42`` on click.
            Defaults to empty string (plain link navigation via ``item.url``).
        empty_message: Message shown in the right panel when no item is
            selected. Defaults to ``"Выберите элемент"``.

    Example::

        from codex_django.cabinet import SplitPanelData, ListRow

        panel = SplitPanelData(
            items=[
                ListRow(
                    id=str(conv.pk),
                    primary=conv.subject,
                    secondary=conv.last_message[:60],
                    meta=conv.updated_at.strftime("%d.%m"),
                    avatar=conv.client_initials,
                )
                for conv in conversations
            ],
            active_id=str(active_conversation.pk) if active_conversation else "",
            detail_url="/cabinet/conversations",
            empty_message="Выберите переписку",
        )
        return render(request, "conversations/index.html", {"panel": panel})
    """

    items: list[ListRow]
    active_id: str = ""
    detail_url: str = ""
    empty_message: str = "Выберите элемент"


# ---------------------------------------------------------------------------
# Booking Widgets
# ---------------------------------------------------------------------------


@dataclass
class ServiceItem:
    """A single service or product in a selector.

    Attributes:
        id: Unique ID (e.g. PK).
        title: Display name (e.g. "Маникюр + Гель-лак").
        price: Price string (e.g. "45").
        duration: Duration in minutes (e.g. 90).
        category: Machine name for filtering (e.g. "nails").
    """

    id: str
    title: str
    price: str
    duration: int
    category: str = "all"
    description: str = ""
    master_ids: list[int] = field(default_factory=list)
    exclusive_group: str = ""
    conflicts_with: list[str] = field(default_factory=list)
    replacement_mode: str = "replace"


@dataclass
class ServiceSelectorData:
    """Payload for ``components/widgets/service_selector.html``.

    Attributes:
        items: List of :class:`ServiceItem`.
        categories: Ordered list of ``(key, label)`` for filters.
        search_placeholder: Placeholder for the search input.
    """

    items: list[ServiceItem]
    categories: list[tuple[str, str]] = field(default_factory=list)
    search_placeholder: str = "Search services..."


@dataclass
class ClientSelectorData:
    """Payload for ``components/widgets/client_selector.html``.

    Attributes:
        clients: List of existing clients for search/selection.
        search_placeholder: Placeholder for the search input.
    """

    clients: list[dict[str, Any]] = field(default_factory=list)
    search_placeholder: str = "Search by name or phone..."


@dataclass
class DateTimePickerData:
    """Payload for ``components/widgets/date_time_picker.html``.

    Attributes:
        available_days: List of days to show in the mini-calendar.
        calendar_cells: Full calendar grid cells including blank placeholders.
        time_slots: List of time strings (e.g. "08:00").
        busy_slots: List of time strings that are unavailable.
        current_month: Month label (e.g. "March 2026").
    """

    available_days: list[dict[str, Any]]
    time_slots: list[str]
    calendar_cells: list[dict[str, Any]] = field(default_factory=list)
    busy_slots: list[str] = field(default_factory=list)
    current_month: str = ""
    default_date: str = ""
    slot_matrix_json: str = "{}"


@dataclass
class BookingSummaryData:
    """Payload for ``components/widgets/summary_panel.html``.

    Attributes:
        confirm_url: POST endpoint for the booking.
        reset_url: URL to clear the selection.
        masters: List of available specialists for manual assignment.
    """

    confirm_url: str
    reset_url: str = ""
    masters: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class BookingQuickCreateServiceOption:
    """Service option shown inside a quick-create booking modal."""

    value: str
    label: str
    price_label: str = ""
    duration_label: str = ""


@dataclass
class BookingQuickCreateClientOption:
    """Client option shown inside a quick-create booking modal."""

    value: str
    label: str
    subtitle: str = ""
    email: str = ""
    search_text: str = ""


@dataclass
class BookingQuickCreateData:
    """Payload for a quick-create single-appointment block inside a modal."""

    resource_label: str
    date_label: str
    time_label: str
    resource_id: str = ""
    booking_date: str = ""
    selected_time: str = ""
    service_options: list[BookingQuickCreateServiceOption] = field(default_factory=list)
    client_options: list[BookingQuickCreateClientOption] = field(default_factory=list)
    selected_service_id: str = ""
    selected_client_id: str = ""
    client_search_query: str = ""
    client_search_min_chars: int = 3
    new_client_first_name: str = ""
    new_client_last_name: str = ""
    new_client_phone: str = ""
    new_client_email: str = ""
    allow_new_client: bool = True


@dataclass
class BookingSlotPickerOption:
    """Single slot option in a booking slot-picker block."""

    value: str
    label: str
    available: bool = True


@dataclass
class BookingSlotPickerData:
    """Payload for a booking-native date navigation and slot selection block."""

    selected_date: str
    selected_date_label: str
    selected_time: str = ""
    prev_url: str = ""
    next_url: str = ""
    today_url: str = ""
    calendar_url: str = ""
    slots: list[BookingSlotPickerOption] = field(default_factory=list)


@dataclass
class BookingChainPreviewItem:
    """Single row in a booking chain preview block."""

    title: str
    subtitle: str = ""
    meta: str = ""


@dataclass
class BookingChainPreviewData:
    """Payload for a booking chain preview block."""

    title: str = "Chain preview"
    items: list[BookingChainPreviewItem] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Modular Modal System
# ---------------------------------------------------------------------------


@dataclass
class ModalSection:
    """Base class for modal sections."""

    type: str = "base"


@dataclass
class ProfileSection(ModalSection):
    """Client/Staff profile header in a modal."""

    name: str = ""
    subtitle: str = ""
    avatar: str = ""
    type: str = "profile"


@dataclass
class KeyValueItem:
    label: str
    value: str


@dataclass
class SummarySection(ModalSection):
    """Grid of key-value pairs (e.g. Appointment details)."""

    items: list[KeyValueItem] = field(default_factory=list)
    type: str = "summary"


@dataclass
class FormField:
    name: str
    label: str
    field_type: str = "text"  # "text" | "textarea" | "select"
    placeholder: str = ""
    value: str = ""
    options: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class FormSection(ModalSection):
    """Input fields group."""

    fields: list[FormField] = field(default_factory=list)
    type: str = "form"


@dataclass
class ModalAction:
    """A button in the modal footer or action group."""

    label: str
    url: str = ""
    method: str = "GET"  # "GET" | "POST" | "CLOSE"
    style: str = "btn-primary"  # "btn-primary" | "btn-secondary" | "btn-danger"
    icon: str = ""


@dataclass
class ActionSection(ModalSection):
    """Group of action buttons."""

    actions: list[ModalAction] = field(default_factory=list)
    type: str = "actions"


@dataclass
class SlotPickerSection(ModalSection):
    """Booking-native date navigator and slot picker for modal workflows."""

    data: BookingSlotPickerData = field(
        default_factory=lambda: BookingSlotPickerData(selected_date="", selected_date_label="")
    )
    type: str = "slot_picker"


@dataclass
class QuickCreateSection(ModalSection):
    """Booking quick-create block for creating one appointment from a calendar slot."""

    data: BookingQuickCreateData = field(
        default_factory=lambda: BookingQuickCreateData(resource_label="", date_label="", time_label="")
    )
    type: str = "quick_create"


@dataclass
class ChainPreviewSection(ModalSection):
    """Booking chain preview block used by richer booking builders/modals."""

    data: BookingChainPreviewData = field(default_factory=BookingChainPreviewData)
    type: str = "chain_preview"


@dataclass
class ModalContentData:
    """Payload for ``components/generic_modal.html``.

    Assembles a modal window from multiple functional sections.
    """

    title: str
    sections: list[ModalSection] = field(default_factory=list)
