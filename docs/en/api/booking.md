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

The full selector, adapter, and mixin-level documentation lives in [Booking internals](internal/booking.md).
