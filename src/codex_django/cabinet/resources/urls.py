"""URL helpers for generic cabinet resources."""

from __future__ import annotations

from django.urls import NoReverseMatch, reverse


def resource_url(name: str, **kwargs: object) -> str:
    """Reverse a cabinet resource route with or without a project namespace."""
    for route_name in (f"cabinet:{name}", name):
        try:
            return reverse(route_name, kwargs=kwargs)
        except NoReverseMatch:
            continue
    raise NoReverseMatch(f"Could not reverse cabinet resource route '{name}'")
