from __future__ import annotations

import subprocess
import sys
import venv
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def blueprints_dir() -> Path:
    return PROJECT_ROOT / "src" / "codex_django" / "cli" / "blueprints"


@pytest.fixture
def sterile_env(tmp_path: Path) -> dict:
    """
    Install the package in an isolated venv for subprocess-based E2E tests.
    Returns a dict with: work_dir, python, cli.
    """
    venv_dir = tmp_path / ".venv"
    venv.create(str(venv_dir), with_pip=True)

    if sys.platform == "win32":
        python = venv_dir / "Scripts" / "python.exe"
        cli = venv_dir / "Scripts" / "codex-django.exe"
    else:
        python = venv_dir / "bin" / "python"
        cli = venv_dir / "bin" / "codex-django"

    subprocess.run(
        [str(python), "-m", "pip", "install", "--quiet", "-e", str(PROJECT_ROOT)],
        check=True,
    )

    work_dir = tmp_path / "project"
    work_dir.mkdir()

    return {"work_dir": work_dir, "python": python, "cli": cli}
