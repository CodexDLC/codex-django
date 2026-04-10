"""Django admin integration for tracking snapshots."""

from __future__ import annotations

from django.contrib import admin

from .models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Inspect flushed page view snapshots."""

    list_display = ("date", "path", "views")
    list_filter = ("date",)
    search_fields = ("path",)
    ordering = ("-date", "-views", "path")
