<!-- DOC_TYPE: GUIDE -->

# Cabinet Guide

## When To Use It

Use `cabinet` when you need a reusable dashboard shell with navigation, widgets, and
typed page components. Cabinet provides the layout and structural templates; your
feature apps contribute navigation entries and build page data using typed contracts.

## Installation

Add to `INSTALLED_APPS` and connect the context processor:

```python
INSTALLED_APPS = [
    ...
    "codex_django.cabinet",
    "cabinet",  # your project-level cabinet app
]

TEMPLATES = [{
    "OPTIONS": {
        "context_processors": [
            ...
            "codex_django.cabinet.context_processors.cabinet",
        ]
    }
}]
```

## Register a Feature

Create `cabinet.py` in any installed app. `CabinetConfig.ready()` discovers it
automatically via `autodiscover_modules("cabinet")`.

```python
# features/booking/cabinet.py
from codex_django.cabinet import declare, TopbarEntry, SidebarItem, Shortcut

# Staff space
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
```

## Set the Active Module in a View

The context processor reads `request.cabinet_module` to know which sidebar to show.
Set it at the top of any cabinet view:

```python
def schedule_view(request):
    request.cabinet_module = "booking"
    ...
    return render(request, "booking/schedule.html", context)
```

If not set, the module is auto-detected from the URL namespace (`request.resolver_match.app_name`),
with `"admin"` as the final fallback.

## Use a Page Component

Build a typed contract in the view, pass it to the template, include the component.

### Data Table

```python
# view
from codex_django.cabinet import DataTableData, TableColumn, TableFilter, TableAction

def appointments_view(request):
    request.cabinet_module = "booking"
    table = DataTableData(
        columns=[
            TableColumn(key="client", label="Client", bold=True),
            TableColumn(key="date",   label="Date"),
            TableColumn(key="status", label="Status"),
        ],
        rows=list(Appointment.objects.values("client", "date", "status", "detail_url")),
        filters=[
            TableFilter(key="pending",   label="Pending",   value="pending"),
            TableFilter(key="confirmed", label="Confirmed", value="confirmed"),
        ],
        actions=[TableAction(label="Open", url_key="detail_url", icon="bi-eye")],
        search_placeholder="Search...",
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

### Calendar Grid

Columns and rows can be anything — masters, rooms, weekdays.
The backend computes `CalendarSlot.span` from duration; the template only renders.

```python
from codex_django.cabinet import CalendarGridData, CalendarSlot

# 30-minute slots from 08:00 to 20:00
rows = [f"{h}:{m:02d}" for h in range(8, 20) for m in (0, 30)]

calendar = CalendarGridData(
    cols=["Master 1", "Master 2", "Master 3"],
    rows=rows,
    events=[
        CalendarSlot(
            col=0, row=2, span=2,       # col index, row index, duration/slot_size
            title="Ivan P.", subtitle="Haircut",
            color="#6366f1", url="/booking/42/",
        ),
    ],
    slot_height_px=40,
    new_event_url="/booking/new/",      # hx-get on empty slot click
)
return render(request, "booking/schedule.html", {"calendar": calendar})
```

```django
{% extends "cabinet/base_cabinet.html" %}
{% block content %}
  {% include "cabinet/components/calendar_grid.html" with calendar=calendar %}
  {% include "cabinet/includes/_modal_base.html" %}
{% endblock %}
```

### Card Grid

```python
from codex_django.cabinet import CardGridData, CardItem

cards = CardGridData(
    items=[
        CardItem(
            id=str(c.pk),
            title=c.full_name,
            subtitle=c.category,
            avatar=c.initials,
            url=f"/cabinet/clients/{c.pk}/",
            meta=[("bi-telephone", c.phone)],
        )
        for c in Client.objects.all()
    ],
    search_placeholder="Search clients...",
)
```

```django
{% include "cabinet/components/card_grid.html" with cards=cards %}
```

### Split Panel

```python
from codex_django.cabinet import SplitPanelData, ListRow

panel = SplitPanelData(
    items=[
        ListRow(id=str(c.pk), primary=c.subject, secondary=c.last_message[:60])
        for c in conversations
    ],
    detail_url="/cabinet/conversations",  # appends /<id> on click
    empty_message="Select a conversation",
)
```

```django
{% include "cabinet/components/split_panel.html" with panel=panel %}
```

## Client Space

Register a separate `declare(space="client", ...)` call and extend `base_client.html`:

```python
declare(
    space="client",
    module="booking",
    sidebar=[
        SidebarItem(label="My Appointments", url="booking:my_bookings",
                    icon="bi-calendar2-check"),
    ],
)
```

```django
{# my_appointments.html #}
{% extends "cabinet/base_client.html" %}
{% block content %}
  {% include "cabinet/components/data_table.html" with table=table %}
{% endblock %}
```

Client-space CSS tokens are overridden independently via `.cab-wrapper--client { --cab-* }` in the project's `theme/tokens.css`.

## Available Components

| Template | Contract | Use for |
|----------|---------|---------|
| `cabinet/components/data_table.html` | `DataTableData` | Filterable tables |
| `cabinet/components/calendar_grid.html` | `CalendarGridData` | Scheduling grids |
| `cabinet/components/card_grid.html` | `CardGridData` | Client/item cards |
| `cabinet/components/list_view.html` | `ListViewData` | Simple lists |
| `cabinet/components/split_panel.html` | `SplitPanelData` | Conversation/detail views |

## Runtime Entry Points

- `codex_django.cabinet`
- `codex_django.cabinet.selector`
- `codex_django.cabinet.redis`

## Related Reading

- Architecture: [Cabinet Module](../architecture/cabinet.md)
- API reference: [Cabinet Public API](../api/cabinet.md)
- Internals: [Cabinet Internal Modules](../api/internal/cabinet.md)
