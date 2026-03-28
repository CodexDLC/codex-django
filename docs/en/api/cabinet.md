<!-- DOC_TYPE: API -->

# Cabinet Public API

The cabinet package exposes the registration API that feature apps use to contribute navigation and widgets to the cabinet UI.

## Stable imports

```python
from codex_django.cabinet import (
    declare,
    cabinet_registry,
    CabinetSection,
    NavAction,
    TableColumn,
    ListItem,
)
```

## Example

```python
from codex_django.cabinet import CabinetSection, declare

declare(
    module="booking",
    section=CabinetSection(label="Bookings", icon="calendar", url="/cabinet/bookings/"),
)
```

For registry internals, dashboard selectors, Redis managers, and cabinet views, open [Cabinet internals](internal/cabinet.md).
