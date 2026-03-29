"""
Integration tests for the codex_makemessages management command.
Uses --dry-run to verify domain discovery and command structure
without requiring gettext or running actual makemessages.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from django.test import override_settings

from codex_django.core.management.commands.codex_makemessages import Command as MakemessagesCommand


def _run_dry(base_dir: Path, languages: list) -> str:
    """Run codex_makemessages --dry-run and return captured stdout."""
    out = io.StringIO()
    cmd = MakemessagesCommand(stdout=out, stderr=io.StringIO())
    with override_settings(BASE_DIR=base_dir, LANGUAGES=languages):
        cmd.handle(dry_run=True)
    return out.getvalue()


def _make_templates_domain(base: Path, domain: str) -> None:
    """Create templates/<domain>/ with a minimal .html file."""
    d = base / "templates" / domain
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text('{% trans "hello" %}', encoding="utf-8")


def _make_feature_domain(base: Path, feature: str) -> None:
    """Create features/<feature>/templates/ with a minimal .html file."""
    d = base / "features" / feature / "templates"
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text('{% trans "world" %}', encoding="utf-8")


@pytest.mark.unit
class TestCodexMakemessagesDryRun:
    def test_dry_run_discovers_templates_domain(self, tmp_path: Path):
        _make_templates_domain(tmp_path, "main")

        output = _run_dry(tmp_path, [("en", "English"), ("ru", "Russian")])

        assert "main" in output
        assert "common" in output  # always processed

    def test_dry_run_includes_all_languages(self, tmp_path: Path):
        _make_templates_domain(tmp_path, "cabinet")

        output = _run_dry(tmp_path, [("en", "English"), ("de", "Deutsch"), ("ru", "Russian")])

        assert "-l en" in output
        assert "-l de" in output
        assert "-l ru" in output

    def test_dry_run_discovers_feature_domain(self, tmp_path: Path):
        _make_feature_domain(tmp_path, "blog")

        output = _run_dry(tmp_path, [("en", "English")])

        assert "blog" in output

    def test_dry_run_multiple_domains_all_discovered(self, tmp_path: Path):
        _make_templates_domain(tmp_path, "cabinet")
        _make_templates_domain(tmp_path, "main")
        _make_feature_domain(tmp_path, "shop")

        output = _run_dry(tmp_path, [("en", "English")])

        assert "cabinet" in output
        assert "main" in output
        assert "shop" in output
        assert "common" in output

    def test_no_languages_exits_with_error(self, tmp_path: Path):
        output = _run_dry(tmp_path, [])

        assert "No LANGUAGES" in output
