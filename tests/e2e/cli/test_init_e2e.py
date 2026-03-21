"""E2E tests for the CLI — run via subprocess in an isolated venv."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.mark.e2e
def test_init_creates_project_structure(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    result = subprocess.run(
        [str(cli), "init", "testproject"],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    project_dir = work_dir / "src" / "testproject"
    assert project_dir.is_dir()
    assert (project_dir / "manage.py").exists()
    assert (project_dir / "core").is_dir()
    assert (project_dir / "features" / "system").is_dir()
    assert (project_dir / "features" / "cabinet").is_dir()


@pytest.mark.e2e
def test_init_skips_existing_project(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    # Create the target directory before running
    target = work_dir / "src" / "myapp"
    target.mkdir(parents=True)

    result = subprocess.run(
        [str(cli), "init", "myapp"],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
    )

    # Should not fail but should warn
    assert result.returncode == 0
    assert (target / "manage.py").not_exists() if hasattr(Path, "not_exists") else not (target / "manage.py").exists()


@pytest.mark.e2e
def test_add_app_creates_app_structure(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    # First init a project
    subprocess.run([str(cli), "init", "myproject"], cwd=str(work_dir), check=True)

    # Then add an app
    project_src = work_dir / "src" / "myproject"
    result = subprocess.run(
        [str(cli), "add-app", "blog"],
        cwd=str(project_src),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    app_dir = project_src / "features" / "blog"
    assert app_dir.is_dir()
    assert (app_dir / "apps.py").exists()
    assert (app_dir / "models" / "__init__.py").exists()
    assert (app_dir / "views" / "__init__.py").exists()


@pytest.mark.e2e
def test_cli_help_exits_cleanly(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    result = subprocess.run(
        [str(cli), "--help"],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
