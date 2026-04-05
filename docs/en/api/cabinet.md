<!-- DOC_TYPE: API -->

# Cabinet Public API

The cabinet package exposes the registration API that feature apps use to contribute
navigation and widgets to the cabinet UI, plus typed data contracts for page components.

## Stable imports

### Navigation & registration

```python
from codex_django.cabinet import (
    declare,
    cabinet_registry,
    TopbarEntry,
    SidebarItem,
    Shortcut,
)
```

### Page component contracts

```python
from codex_django.cabinet import (
    DataTableData,
    TableColumn,
    TableFilter,
    TableAction,
    CalendarGridData,
    CalendarSlot,
    CardGridData,
    CardItem,
    ListViewData,
    ListRow,
    SplitPanelData,
)
```

### Dashboard widget contracts

```python
from codex_django.cabinet import (
    MetricWidgetData,
    TableWidgetData,
    ListWidgetData,
    DashboardWidget,
)
```

### Legacy v1 (backward compatible)

```python
from codex_django.cabinet import CabinetSection, NavAction
```

## Examples

### Register a feature (staff + client spaces)

```python
# features/booking/cabinet.py
from codex_django.cabinet import declare, TopbarEntry, SidebarItem, Shortcut

# Staff space — topbar entry + sidebar navigation
declare(
    space="staff",
    module="booking",
    topbar=TopbarEntry(
        group="services",
        label="Booking",
        icon="bi-calendar-check",
        url="/cabinet/booking/",
        order=10,
    ),
    sidebar=[
        SidebarItem(label="Schedule",    url="booking:schedule",   icon="bi-calendar3"),
        SidebarItem(label="New Booking", url="booking:new",        icon="bi-plus-circle"),
        SidebarItem(label="Pending",     url="booking:pending",    icon="bi-hourglass-split",
                    badge_key="pending_count"),
    ],
    shortcuts=[
        Shortcut(label="New", url="booking:new", icon="bi-plus"),
    ],
)

# Client space — sidebar only
declare(
    space="client",
    module="booking",
    sidebar=[
        SidebarItem(label="My Appointments", url="booking:my_bookings",
                    icon="bi-calendar2-check"),
    ],
)
```

### Use a page component in a view

```python
# features/booking/views/appointments.py
from codex_django.cabinet import DataTableData, TableColumn, TableFilter, TableAction

def appointments_view(request):
    request.cabinet_module = "booking"

    table = DataTableData(
        columns=[
            TableColumn(key="client",  label="Client",  bold=True),
            TableColumn(key="date",    label="Date"),
            TableColumn(key="status",  label="Status",  badge_key="status_colors"),
        ],
        rows=list(
            Appointment.objects.values("client", "date", "status", "detail_url")
        ),
        filters=[
            TableFilter(key="pending",   label="Pending",   value="pending"),
            TableFilter(key="confirmed", label="Confirmed", value="confirmed"),
        ],
        actions=[TableAction(label="Open", url_key="detail_url", icon="bi-eye")],
        search_placeholder="Search appointments...",
    )
    return render(request, "booking/appointments.html", {"table": table})
```

```django
{# booking/appointments.html #}
{% extends "cabinet/base_cabinet.html" %}
{% block content %}
  {% include "cabinet/components/data_table.html" with table=table %}
  {% include "cabinet/includes/_modal_base.html" %}
{% endblock %}
```

### Calendar component

```python
from codex_django.cabinet import CalendarGridData, CalendarSlot

rows = [f"{h}:{m:02d}" for h in range(8, 20) for m in (0, 30)]

calendar = CalendarGridData(
    cols=["Master 1", "Master 2", "Master 3"],
    rows=rows,
    events=[
        CalendarSlot(col=0, row=2, span=2, title="Ivan P.", subtitle="Haircut",
                     color="#6366f1", url="/booking/42/"),
    ],
    new_event_url="/booking/new/",
)
return render(request, "booking/schedule.html", {"calendar": calendar})
```

```django
{% include "cabinet/components/calendar_grid.html" with calendar=calendar %}
{% include "cabinet/includes/_modal_base.html" %}
```

For registry internals, dashboard selectors, Redis managers, and cabinet views,
see [Cabinet internals](internal/cabinet.md).
