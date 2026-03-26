"""Unit tests for CLIEngine."""

from __future__ import annotations

from pathlib import Path

import pytest

from codex_django.cli.engine import CLIEngine


@pytest.mark.unit
class TestCLIEngineInit:
    def test_default_blueprints_dir(self):
        engine = CLIEngine()
        assert Path(engine.blueprints_dir).is_dir()
        assert Path(engine.blueprints_dir).name == "blueprints"

    def test_custom_blueprints_dir(self, tmp_path: Path):
        engine = CLIEngine(blueprints_dir=str(tmp_path))
        assert engine.blueprints_dir == str(tmp_path)


@pytest.mark.unit
class TestRenderTemplate:
    def test_renders_variable(self, tmp_path: Path):
        (tmp_path / "hello.j2").write_text("Hello {{ name }}!")
        engine = CLIEngine(blueprints_dir=str(tmp_path))
        result = engine.render_template("hello.j2", {"name": "World"})
        assert result == "Hello World!"

    def test_renders_empty_context(self, tmp_path: Path):
        (tmp_path / "static.j2").write_text("no vars here")
        engine = CLIEngine(blueprints_dir=str(tmp_path))
        assert engine.render_template("static.j2", {}) == "no vars here"

    def test_raises_on_missing_template(self, tmp_path: Path):
        engine = CLIEngine(blueprints_dir=str(tmp_path))
        with pytest.raises(ValueError):
            engine.render_template("nonexistent.j2", {})


@pytest.mark.unit
class TestScaffold:
    def _make_blueprint(self, blueprints_dir: Path, name: str) -> Path:
        bp = blueprints_dir / name
        bp.mkdir(parents=True)
        return bp

    def test_creates_plain_file(self, tmp_path: Path):
        bp_dir = tmp_path / "blueprints"
        bp = self._make_blueprint(bp_dir, "myblueprint")
        (bp / "readme.txt").write_text("hello")

        engine = CLIEngine(blueprints_dir=str(bp_dir))
        target = tmp_path / "output"
        engine.scaffold("myblueprint", str(target), {})

        assert (target / "readme.txt").read_text() == "hello"

    def test_renders_j2_and_strips_extension(self, tmp_path: Path):
        bp_dir = tmp_path / "blueprints"
        bp = self._make_blueprint(bp_dir, "myblueprint")
        (bp / "apps.py.j2").write_text("name = '{{ app_name }}'")

        engine = CLIEngine(blueprints_dir=str(bp_dir))
        target = tmp_path / "output"
        engine.scaffold("myblueprint", str(target), {"app_name": "blog"})

        assert (target / "apps.py").read_text() == "name = 'blog'"
        assert not (target / "apps.py.j2").exists()

    def test_scaffold_creates_nested_dirs(self, tmp_path: Path):
        bp_dir = tmp_path / "blueprints"
        bp = self._make_blueprint(bp_dir, "myblueprint")
        sub = bp / "models"
        sub.mkdir()
        (sub / "__init__.py").write_text("")

        engine = CLIEngine(blueprints_dir=str(bp_dir))
        target = tmp_path / "output"
        engine.scaffold("myblueprint", str(target), {})

        assert (target / "models" / "__init__.py").exists()

    def test_skips_existing_file_by_default(self, tmp_path: Path):
        bp_dir = tmp_path / "blueprints"
        bp = self._make_blueprint(bp_dir, "myblueprint")
        (bp / "file.txt").write_text("new content")

        target = tmp_path / "output"
        target.mkdir()
        (target / "file.txt").write_text("original content")

        engine = CLIEngine(blueprints_dir=str(bp_dir))
        engine.scaffold("myblueprint", str(target), {}, overwrite=False)

        assert (target / "file.txt").read_text() == "original content"

    def test_overwrites_existing_file_when_flag_set(self, tmp_path: Path):
        bp_dir = tmp_path / "blueprints"
        bp = self._make_blueprint(bp_dir, "myblueprint")
        (bp / "file.txt").write_text("new content")

        target = tmp_path / "output"
        target.mkdir()
        (target / "file.txt").write_text("original content")

        engine = CLIEngine(blueprints_dir=str(bp_dir))
        engine.scaffold("myblueprint", str(target), {}, overwrite=True)

        assert (target / "file.txt").read_text() == "new content"

    def test_raises_on_missing_blueprint(self, tmp_path: Path):
        bp_dir = tmp_path / "blueprints"
        bp_dir.mkdir()
        engine = CLIEngine(blueprints_dir=str(bp_dir))

        with pytest.raises(ValueError, match="Blueprint 'missing' not found"):
            engine.scaffold("missing", str(tmp_path / "output"), {})


@pytest.mark.unit
class TestScaffoldRealBlueprints:
    """Smoke tests against the real blueprints directory."""

    def test_scaffold_apps_default(self, tmp_path: Path):
        engine = CLIEngine()
        engine.scaffold("apps/default", str(tmp_path / "blog"), {"app_name": "blog"})
        assert (tmp_path / "blog" / "apps.py").exists()
        assert (tmp_path / "blog" / "models" / "__init__.py").exists()

    def test_scaffold_notifications_feature(self, tmp_path: Path):
        engine = CLIEngine()
        engine.scaffold(
            "features/notifications/feature",
            str(tmp_path / "system"),
            {"app_name": "system"},
        )
        # Note: notification blueprints use `email_content.j2` (not `.py.j2`),
        # so the engine strips `.j2` and produces a file without extension.
        assert (tmp_path / "system" / "models" / "email_content").exists()
        assert (tmp_path / "system" / "services" / "notification").exists()
