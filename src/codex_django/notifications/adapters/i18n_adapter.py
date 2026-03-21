"""
DjangoI18nAdapter
=================
Provides language override context manager for notification content lookup.

Usage::

    adapter = DjangoI18nAdapter()
    with adapter.translation_override("de"):
        subject = EmailContent.objects.get(key="booking_subject").text
"""

from __future__ import annotations

from contextlib import AbstractContextManager


class DjangoI18nAdapter:
    """Wraps Django's translation.override() for notification language switching."""

    def translation_override(self, language: str) -> AbstractContextManager[None]:
        from django.utils.translation import override

        return override(language)
