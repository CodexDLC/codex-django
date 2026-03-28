"""Compatibility shims for the split-out codex-django CLI package."""

from __future__ import annotations

from typing import Any

from codex_django.cli._compat import load_cli_module


def main(*args: Any, **kwargs: Any) -> int:
    """Lazily dispatch to the real CLI entrypoint from codex-django-cli."""
    return load_cli_module("main").main(*args, **kwargs)


__all__ = ["main"]
