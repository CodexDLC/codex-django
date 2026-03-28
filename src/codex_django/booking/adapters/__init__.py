"""Booking adapter exports.

The booking adapter layer translates between project-specific Django models
and the generic booking engine / cache infrastructure.
"""

from .availability import DjangoAvailabilityAdapter
from .cache import BookingCacheAdapter

__all__ = [
    "BookingCacheAdapter",
    "DjangoAvailabilityAdapter",
]
