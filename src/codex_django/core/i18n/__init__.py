"""Internationalization helpers for codex-django projects."""

from .discovery import discover_locale_paths, translate_current_url

__all__ = ["discover_locale_paths", "translate_current_url"]
