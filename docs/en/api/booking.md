<!-- DOC_TYPE: API -->

# Booking Public API

The booking package is organized around reusable abstract models plus adapters that connect Django data to the booking engine.

## Stable imports

```python
from codex_django.booking import (
    DjangoAvailabilityAdapter,
    BookingCacheAdapter,
    AbstractBookableMaster,
    AbstractBookableService,
    AbstractBookableAppointment,
    AbstractWorkingDay,
    MasterDayOffMixin,
    AbstractBookingSettings,
)
```

## Typical flow

1. Compose project models from the exported booking mixins.
2. Use `DjangoAvailabilityAdapter` to bridge ORM data into the engine.
3. Call selector functions from the internal booking layer in your views or services.

## Public naming policy (`>=0.3.0`)

Public selector and gateway contracts use neutral resource naming:

- `resource_id`
- `resource_selections`
- `locked_resource_id`

Legacy `master_*` argument names are not part of the public runtime API starting from `0.3.0`.

The full selector, adapter, and mixin-level documentation lives in [Booking internals](internal/booking.md).
