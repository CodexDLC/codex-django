from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import NoReturn


def raise_cli_dependency_error(exc: ModuleNotFoundError) -> NoReturn:
    """Raise a helpful error when the split-out CLI package is unavailable."""
    if exc.name and exc.name.startswith("codex_django_cli"):
        raise ModuleNotFoundError(
            "codex-django CLI moved into the optional 'codex-django-cli' package. "
            "Install 'codex-django-cli' to use codex_django.cli."
        ) from exc
    raise exc


def load_cli_module(module_name: str) -> ModuleType:
    """Import a module from codex_django_cli and normalize missing-dependency errors."""
    try:
        return import_module(f"codex_django_cli.{module_name}")
    except ModuleNotFoundError as exc:  # pragma: no cover - exercised when extra is absent
        raise_cli_dependency_error(exc)
