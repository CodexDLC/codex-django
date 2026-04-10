"""Reusable class-based view helpers for cabinet modules."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import TemplateView


class CabinetModuleMixin(View):
    """Attach cabinet metadata to the request before rendering a view."""

    cabinet_space = "staff"
    cabinet_module = ""
    cabinet_nav_group: str | None = None

    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        if self.cabinet_space:
            request.cabinet_space = self.cabinet_space
        if self.cabinet_module:
            request.cabinet_module = self.cabinet_module
        if self.cabinet_nav_group is not None:
            request.cabinet_nav_group = self.cabinet_nav_group
        return super().dispatch(request, *args, **kwargs)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require an authenticated staff or superuser account."""

    raise_exception = True

    def test_func(self) -> bool:
        request = getattr(self, "request", None)
        user = getattr(request, "user", None)
        return bool(
            getattr(user, "is_active", False)
            and (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))
        )


class OwnerRequiredMixin(StaffRequiredMixin):
    """Require an authenticated owner/superuser account."""

    def test_func(self) -> bool:
        request = getattr(self, "request", None)
        user = getattr(request, "user", None)
        return bool(getattr(user, "is_active", False) and getattr(user, "is_superuser", False))


class CabinetTemplateView(CabinetModuleMixin, TemplateView):
    """TemplateView with cabinet request metadata support."""
