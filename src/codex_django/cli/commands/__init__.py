"""Compatibility shims for codex-django CLI command handlers."""

from __future__ import annotations

import sys

from codex_django.cli._compat import load_cli_module

sys.modules[__name__] = load_cli_module("commands")
