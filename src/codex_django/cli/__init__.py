"""Compatibility shims for the split-out codex-django CLI package."""

from __future__ import annotations

from typing import Any, Protocol, cast

from codex_django.cli._compat import load_cli_module


class _MainModule(Protocol):
    def main(self, *args: Any, **kwargs: Any) -> int: ...


def main(*args: Any, **kwargs: Any) -> int:
    """Lazily dispatch to the real CLI entrypoint from codex-django-cli."""
    module = cast(_MainModule, load_cli_module("main"))
    return module.main(*args, **kwargs)


__all__ = ["main"]
