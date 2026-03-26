"""Integration test: scaffolded project must pass ruff and bandit."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from codex_django.cli.commands.init import handle_init


@pytest.mark.integration
class TestScaffoldQuality:
    """Verify that a freshly scaffolded project passes linting tools."""

    def test_scaffolded_project_passes_ruff(self, tmp_path: Path) -> None:
        # handle_init creates: tmp_path/<name>/  (with pyproject.toml and src/<name>/)
        handle_init("testproject", str(tmp_path))
        project_root = tmp_path / "testproject"

        # Auto-fix what can be fixed (import sorting, etc.) — matches codex-bot pattern
        subprocess.run(
            [sys.executable, "-m", "ruff", "check", "--fix", "."],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )

        # Assert no remaining issues — ruff discovers config from generated pyproject.toml
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "."],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0, (
            f"ruff found issues in scaffolded project:\n{result.stdout}\n{result.stderr}"
        )

    def test_scaffolded_project_passes_bandit(self, tmp_path: Path) -> None:
        handle_init("testproject", str(tmp_path))
        project_root = tmp_path / "testproject"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bandit",
                "-r",
                str(project_root),
                "-ll",  # only medium/high severity
                "--skip",
                "B404",  # subprocess import — intentional in menu.py
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"bandit found issues in scaffolded project:\n{result.stdout}\n{result.stderr}"
        )
