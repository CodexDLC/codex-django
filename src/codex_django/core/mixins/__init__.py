"""Public exports for reusable core model mixins.

Examples:
    Compose a project model from the shared mixins::

        from codex_django.core.mixins import TimestampMixin, ActiveMixin, SlugMixin

        class Article(TimestampMixin, ActiveMixin, SlugMixin):
            ...
"""

from .models import (
    ActiveMixin,
    OrderableMixin,
    SeoMixin,
    SlugMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)

__all__ = [
    "TimestampMixin",
    "ActiveMixin",
    "SeoMixin",
    "OrderableMixin",
    "SoftDeleteMixin",
    "UUIDMixin",
    "SlugMixin",
]
