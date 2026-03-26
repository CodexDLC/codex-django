"""Unit tests for CLI command handlers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import ANY, MagicMock, call, patch

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

            # handle_init calls scaffold 3x: repo, deploy, project. secret_key is random → ANY.
            assert mock_engine.scaffold.call_count == 3
            calls = mock_engine.scaffold.call_args_list
            base_context = {
                "project_name": "myproject",
                "secret_key": ANY,
                "multilingual": False,
                "languages": ["en"],
                "with_cabinet": False,
                "with_booking": False,
                "with_notifications": False,
            }
            assert calls[0] == call(
                "repo",
                target_dir=str(tmp_path / "myproject"),
                context=base_context,
                overwrite=False,
            )
            assert calls[1] == call(
                "deploy",
                target_dir=str(tmp_path / "myproject" / "deploy" / "myproject"),
                context=base_context,
                overwrite=False,
            )
            assert calls[2] == call(
                "project",
                target_dir=str(tmp_path / "myproject" / "src" / "myproject"),
                context=base_context,
                overwrite=False,
            )

    def test_skips_if_target_exists(self, tmp_path: Path):
        # handle_init checks for manage.py inside backend_dir to detect an existing project
        manage_py = tmp_path / "myproject" / "src" / "myproject" / "manage.py"
        manage_py.parent.mkdir(parents=True)
        manage_py.write_text("")

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

    def test_target_dir(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django.cli.commands.init import handle_init

            handle_init("myproject", "base_dir", target_dir=str(tmp_path))
            calls = mock_engine.scaffold.call_args_list
            assert calls[0][1]["target_dir"] == str(tmp_path)

    def test_dev_mode_valid(self, tmp_path: Path):
        from unittest.mock import mock_open

        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("os.path.exists", side_effect=lambda path: str(path).endswith("pyproject.toml")),
            patch("builtins.open", mock_open(read_data='name = "codex-django"')),
        ):
            from codex_django.cli.commands.init import handle_init

            handle_init("myproject", "base_dir", dev_mode=True)
            mock_engine_cls.return_value.scaffold.assert_called()

    def test_dev_mode_invalid(self, tmp_path: Path):
        with patch("os.path.exists", return_value=False):
            from codex_django.cli.commands.init import handle_init

            handle_init("myproject", "base_dir", dev_mode=True)

    def test_code_only(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django.cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path), code_only=True)
            assert mock_engine.scaffold.call_count == 1

    def test_multilingual_languages_context(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django.cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path), multilingual=True, languages=["en", "ru", "de"])

            # Verify context passed to engine
            _, kwargs = mock_engine.scaffold.call_args
            context = kwargs["context"]
            assert context["multilingual"] is True
            assert context["languages"] == ["en", "ru", "de"]


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
            assert feature_call[0][0] == "features/notifications/feature"
            assert feature_call[1]["context"] == {"app_name": "system"}

            arq_call = calls[1]
            assert arq_call[0][0] == "features/notifications/arq"
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
