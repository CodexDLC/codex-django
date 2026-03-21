"""
Integration tests for CLI command handlers.

Uses the real CLIEngine (no mocks) — writes actual files to tmp_path.
No subprocess, no external services required.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codex_django.cli.commands.add_app import handle_add_app
from codex_django.cli.commands.init import handle_init
from codex_django.cli.commands.notifications import handle_add_notifications


@pytest.mark.integration
class TestHandleInitIntegration:
    def test_creates_project_structure(self, tmp_path: Path):
        handle_init("myproject", str(tmp_path))

        project = tmp_path / "src" / "myproject"
        assert project.is_dir()
        assert (project / "manage.py").exists()
        assert (project / "core").is_dir()
        assert (project / "system").is_dir()
        assert (project / "cabinet").is_dir()

    def test_creates_core_settings(self, tmp_path: Path):
        handle_init("myproject", str(tmp_path))

        settings_dir = tmp_path / "src" / "myproject" / "core" / "settings"
        assert (settings_dir / "base.py").exists()
        assert (settings_dir / "dev.py").exists()
        assert (settings_dir / "prod.py").exists()

    def test_renders_project_name_in_system_apps(self, tmp_path: Path):
        handle_init("blog_platform", str(tmp_path))

        system_apps = tmp_path / "src" / "blog_platform" / "system" / "apps.py"
        assert system_apps.exists()
        content = system_apps.read_text()
        assert "blog_platform" in content

    def test_skips_existing_project(self, tmp_path: Path):
        target = tmp_path / "src" / "myproject"
        target.mkdir(parents=True)
        sentinel = target / "sentinel.txt"
        sentinel.write_text("original")

        handle_init("myproject", str(tmp_path))

        assert sentinel.read_text() == "original"
        assert not (target / "manage.py").exists()

    def test_idempotent_second_call_skipped(self, tmp_path: Path):
        handle_init("myproject", str(tmp_path))
        manage_py = tmp_path / "src" / "myproject" / "manage.py"
        original_content = manage_py.read_text()

        handle_init("myproject", str(tmp_path))

        assert manage_py.read_text() == original_content


@pytest.mark.integration
class TestHandleAddAppIntegration:
    def test_creates_app_structure(self, tmp_path: Path):
        handle_add_app("blog", str(tmp_path))

        app = tmp_path / "features" / "blog"
        assert app.is_dir()
        assert (app / "apps.py").exists()
        assert (app / "models" / "__init__.py").exists()
        assert (app / "views" / "__init__.py").exists()
        assert (app / "urls.py").exists()

    def test_creates_all_standard_subdirs(self, tmp_path: Path):
        handle_add_app("shop", str(tmp_path))

        app = tmp_path / "features" / "shop"
        for subdir in ("models", "views", "forms", "services", "admin", "tests"):
            assert (app / subdir).is_dir(), f"Missing subdir: {subdir}"

    def test_skips_existing_app(self, tmp_path: Path):
        target = tmp_path / "features" / "blog"
        target.mkdir(parents=True)
        sentinel = target / "sentinel.txt"
        sentinel.write_text("original")

        handle_add_app("blog", str(tmp_path))

        assert sentinel.read_text() == "original"
        assert not (target / "apps.py").exists()

    def test_multiple_apps_independent(self, tmp_path: Path):
        handle_add_app("blog", str(tmp_path))
        handle_add_app("shop", str(tmp_path))

        assert (tmp_path / "features" / "blog" / "apps.py").exists()
        assert (tmp_path / "features" / "shop" / "apps.py").exists()


@pytest.mark.integration
class TestHandleAddNotificationsIntegration:
    def test_creates_feature_and_arq_structure(self, tmp_path: Path):
        handle_add_notifications("system", str(tmp_path))

        feature = tmp_path / "features" / "system"
        assert feature.is_dir()
        # blueprints use .j2 (not .py.j2) so files have no .py extension
        assert (feature / "models" / "email_content").exists()
        assert (feature / "selectors" / "email_content").exists()
        assert (feature / "services" / "notification").exists()

        arq = tmp_path / "core" / "arq"
        assert arq.is_dir()
        assert (arq / "client").exists()

    def test_custom_arq_dir(self, tmp_path: Path):
        handle_add_notifications("alerts", str(tmp_path), arq_dir="workers/arq")

        assert (tmp_path / "features" / "alerts").is_dir()
        assert (tmp_path / "workers" / "arq" / "client").exists()

    def test_renders_app_name_in_model_template(self, tmp_path: Path):
        handle_add_notifications("system", str(tmp_path))

        model_file = tmp_path / "features" / "system" / "models" / "email_content"
        content = model_file.read_text()
        assert "system" in content
