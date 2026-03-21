"""Unit tests for CLI command handlers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# CLIEngine is imported lazily inside each handler function,
# so we patch it at the source module: codex_django.cli.engine.CLIEngine
_ENGINE_PATH = "codex_django.cli.engine.CLIEngine"


@pytest.mark.unit
class TestHandleInit:
    def test_scaffolds_project(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django.cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path))

            mock_engine.scaffold.assert_called_once_with(
                "project",
                target_dir=str(tmp_path / "src" / "myproject"),
                context={"project_name": "myproject"},
            )

    def test_skips_if_target_exists(self, tmp_path: Path):
        target = tmp_path / "src" / "myproject"
        target.mkdir(parents=True)

        with patch(_ENGINE_PATH) as mock_engine_cls:
            from codex_django.cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path))

            mock_engine_cls.return_value.scaffold.assert_not_called()

    def test_uses_correct_project_name_in_context(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django.cli.commands.init import handle_init

            handle_init("my_app", str(tmp_path))

            _, kwargs = mock_engine.scaffold.call_args
            assert kwargs["context"]["project_name"] == "my_app"


@pytest.mark.unit
class TestHandleAddApp:
    def test_scaffolds_app(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django.cli.commands.add_app import handle_add_app

            handle_add_app("blog", str(tmp_path))

            mock_engine.scaffold.assert_called_once_with(
                "apps/default",
                target_dir=str(tmp_path / "features" / "blog"),
                context={"app_name": "blog"},
            )

    def test_skips_if_app_exists(self, tmp_path: Path):
        target = tmp_path / "features" / "blog"
        target.mkdir(parents=True)

        with patch(_ENGINE_PATH) as mock_engine_cls:
            from codex_django.cli.commands.add_app import handle_add_app

            handle_add_app("blog", str(tmp_path))

            mock_engine_cls.return_value.scaffold.assert_not_called()


@pytest.mark.unit
class TestHandleAddNotifications:
    def test_scaffolds_feature_and_arq(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django.cli.commands.notifications import handle_add_notifications

            handle_add_notifications("system", str(tmp_path))

            calls = mock_engine.scaffold.call_args_list
            assert len(calls) == 2

            feature_call = calls[0]
            assert feature_call[0][0] == "notifications/feature"
            assert feature_call[1]["context"] == {"app_name": "system"}

            arq_call = calls[1]
            assert arq_call[0][0] == "notifications/arq"
            assert arq_call[1]["target_dir"] == str(tmp_path / "core" / "arq")

    def test_custom_arq_dir(self, tmp_path: Path):
        import os

        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django.cli.commands.notifications import handle_add_notifications

            handle_add_notifications("system", str(tmp_path), arq_dir="myapp/arq")

            arq_call = mock_engine.scaffold.call_args_list[1]
            # Use os.path.join to match how the handler computes the path
            expected = os.path.join(str(tmp_path), "myapp/arq")
            assert arq_call[1]["target_dir"] == expected
