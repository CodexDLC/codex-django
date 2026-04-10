"""Helpers for discovering Django locale directories.

Examples:
    Resolve locale paths for a generated project root::

        from pathlib import Path
        from codex_django.core.i18n import discover_locale_paths

        LOCALE_PATHS = discover_locale_paths(Path(BASE_DIR))
"""

from pathlib import Path
from typing import Any

from django.urls import translate_url as django_translate_url


def discover_locale_paths(base_dir: Path, include_features: bool = True) -> list[str]:
    """Discover locale directories that should be added to ``LOCALE_PATHS``.

    The helper supports both a centralized ``locale/<domain>/<lang>``
    structure and per-app ``locale/`` directories. Feature apps under
    ``base_dir / "features"`` can be included or skipped explicitly.

    Args:
        base_dir: Project root that contains apps, optional ``locale/``, and
            optional ``features/`` directories.
        include_features: Whether locale directories inside the ``features``
            subtree should be included in the result.

    Returns:
        A list of locale directory paths suitable for Django's
        ``LOCALE_PATHS`` setting. Paths are returned in discovery order and
        are de-duplicated across supported layouts.
    """
    paths = []

    # 1. Check centralized locale directory (for modular domains)
    central_locale = base_dir / "locale"
    if central_locale.exists():
        # A modular domain is a subdirectory that contains <lang>/LC_MESSAGES
        # e.g., locale/cabinet/en/LC_MESSAGES/django.po
        for domain_dir in central_locale.iterdir():
            if domain_dir.is_dir():
                # Check if it has any language subdirectories
                for lang_dir in domain_dir.iterdir():
                    if lang_dir.is_dir() and (lang_dir / "LC_MESSAGES").exists():
                        paths.append(str(domain_dir))
                        break

    # 2. Backward compatibility / alternative structure:
    # Check top-level directories and features for their own locale/ folders
    for item in base_dir.iterdir():
        if item.is_dir() and (item / "locale").exists() and str(item / "locale") not in paths:
            paths.append(str(item / "locale"))

    features_dir = base_dir / "features"
    if include_features and features_dir.exists():
        for item in features_dir.iterdir():
            if item.is_dir() and (item / "locale").exists() and str(item / "locale") not in paths:
                paths.append(str(item / "locale"))

    return paths


def translate_current_url(context: dict[str, Any], lang_code: str) -> str:
    """Translate the current request path into another active language.

    Args:
        context: Template context expected to contain the current ``request``.
        lang_code: Target Django language code.

    Returns:
        The translated URL path for the current request, or an empty string
        when the request/path is unavailable.
    """
    request = context.get("request")
    if not request:
        return ""

    path = getattr(request, "path", "")
    if not path:
        return ""

    return django_translate_url(path, lang_code)
