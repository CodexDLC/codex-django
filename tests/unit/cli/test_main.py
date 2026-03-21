"""Unit tests for CLI main entry point."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

import codex_django.cli.prompts as prompts_module
from codex_django.cli.main import _handle_legacy_args, _interactive_menu, main

# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_main_no_args_calls_interactive_menu():
    with patch("codex_django.cli.main._interactive_menu", return_value=0) as mock_menu:
        result = main([])
        mock_menu.assert_called_once()
        assert result == 0


@pytest.mark.unit
def test_main_none_reads_sys_argv():
    # args=None → reads sys.argv[1:] — line 19
    with (
        patch("codex_django.cli.main.sys.argv", ["codex-django", "init", "testproj"]),
        patch("codex_django.cli.main._handle_legacy_args", return_value=0) as mock_legacy,
    ):
        result = main(None)
        mock_legacy.assert_called_once_with(["init", "testproj"])
        assert result == 0


@pytest.mark.unit
def test_main_with_args_calls_legacy_handler():
    with patch("codex_django.cli.main._handle_legacy_args", return_value=0) as mock_legacy:
        result = main(["init", "myproject"])
        mock_legacy.assert_called_once_with(["init", "myproject"])
        assert result == 0


# ---------------------------------------------------------------------------
# _interactive_menu()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_interactive_menu_exit():
    with patch.object(prompts_module, "ask_main_action", return_value="❌  Exit"):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_none_action():
    with patch.object(prompts_module, "ask_main_action", return_value=None):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_init(tmp_path: Path):
    with (
        patch.object(prompts_module, "ask_main_action", return_value="🚀  Init new project"),
        patch.object(prompts_module, "ask_project_name", return_value="myproject"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.commands.init.handle_init") as mock_handle,
    ):
        result = _interactive_menu()
        mock_handle.assert_called_once_with("myproject", str(tmp_path))
        assert result == 0


@pytest.mark.unit
def test_interactive_menu_init_empty_name():
    with (
        patch.object(prompts_module, "ask_main_action", return_value="🚀  Init new project"),
        patch.object(prompts_module, "ask_project_name", return_value=None),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_add_feature_no_pyproject(tmp_path: Path):
    with (
        patch.object(prompts_module, "ask_main_action", return_value="🧩  Add feature/extension"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.exists", return_value=False),
    ):
        assert _interactive_menu() == 1


@pytest.mark.unit
def test_interactive_menu_add_app(tmp_path: Path):
    src = tmp_path / "src" / "myproject"
    src.mkdir(parents=True)

    with (
        patch.object(prompts_module, "ask_main_action", return_value="🧩  Add feature/extension"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.exists", return_value=True),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch.object(prompts_module, "ask_target_project", return_value="myproject"),
        patch.object(prompts_module, "ask_feature", return_value="Basic app"),
        patch.object(prompts_module, "ask_app_name", return_value="blog"),
        patch("codex_django.cli.commands.add_app.handle_add_app") as mock_handle,
    ):
        result = _interactive_menu()
        mock_handle.assert_called_once()
        assert result == 0


@pytest.mark.unit
def test_interactive_menu_add_notifications(tmp_path: Path):
    with (
        patch.object(prompts_module, "ask_main_action", return_value="🧩  Add feature/extension"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.exists", return_value=True),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch.object(prompts_module, "ask_target_project", return_value="myproject"),
        patch.object(prompts_module, "ask_feature", return_value="Notifications"),
        patch.object(prompts_module, "ask_app_name", return_value="system"),
        patch("codex_django.cli.commands.notifications.handle_add_notifications") as mock_handle,
    ):
        result = _interactive_menu()
        mock_handle.assert_called_once()
        assert result == 0


@pytest.mark.unit
def test_interactive_menu_back_from_feature():
    with (
        patch.object(prompts_module, "ask_main_action", return_value="🧩  Add feature/extension"),
        patch("codex_django.cli.main.os.path.exists", return_value=True),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch.object(prompts_module, "ask_target_project", return_value="myproject"),
        patch.object(prompts_module, "ask_feature", return_value="← Back"),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_no_src_dir(tmp_path: Path):
    # pyproject.toml exists, but src/ is not a directory — line 48-49
    with (
        patch.object(prompts_module, "ask_main_action", return_value="🧩  Add feature/extension"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.exists", return_value=True),
        patch("codex_django.cli.main.os.path.isdir", return_value=False),
    ):
        assert _interactive_menu() == 1


@pytest.mark.unit
def test_interactive_menu_empty_src_dir(tmp_path: Path):
    # src/ exists but has no projects — line 53-54
    with (
        patch.object(prompts_module, "ask_main_action", return_value="🧩  Add feature/extension"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.exists", return_value=True),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=[]),
    ):
        assert _interactive_menu() == 1


@pytest.mark.unit
def test_interactive_menu_target_project_none(tmp_path: Path):
    # ask_target_project returns None (user pressed Ctrl+C) — line 58
    with (
        patch.object(prompts_module, "ask_main_action", return_value="🧩  Add feature/extension"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.exists", return_value=True),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch.object(prompts_module, "ask_target_project", return_value=None),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_basic_app_empty_name(tmp_path: Path):
    # ask_app_name returns None for "Basic app" — line 67
    with (
        patch.object(prompts_module, "ask_main_action", return_value="🧩  Add feature/extension"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.exists", return_value=True),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch.object(prompts_module, "ask_target_project", return_value="myproject"),
        patch.object(prompts_module, "ask_feature", return_value="Basic app"),
        patch.object(prompts_module, "ask_app_name", return_value=None),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_notifications_empty_name(tmp_path: Path):
    # ask_app_name returns None for "Notifications" — line 75
    with (
        patch.object(prompts_module, "ask_main_action", return_value="🧩  Add feature/extension"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.exists", return_value=True),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch.object(prompts_module, "ask_target_project", return_value="myproject"),
        patch.object(prompts_module, "ask_feature", return_value="Notifications"),
        patch.object(prompts_module, "ask_app_name", return_value=None),
    ):
        assert _interactive_menu() == 0


# ---------------------------------------------------------------------------
# _handle_legacy_args()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_legacy_init(tmp_path: Path):
    with (
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.commands.init.handle_init") as mock_handle,
    ):
        result = _handle_legacy_args(["init", "myproject"])
        mock_handle.assert_called_once_with("myproject", str(tmp_path))
        assert result == 0


@pytest.mark.unit
def test_legacy_add_app_with_project(tmp_path: Path):
    with (
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.commands.add_app.handle_add_app") as mock_handle,
    ):
        result = _handle_legacy_args(["add-app", "blog", "--project", "myapp"])
        mock_handle.assert_called_once_with("blog", str(tmp_path / "src" / "myapp"))
        assert result == 0


@pytest.mark.unit
def test_legacy_add_app_without_project(tmp_path: Path):
    with (
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.commands.add_app.handle_add_app") as mock_handle,
    ):
        result = _handle_legacy_args(["add-app", "blog"])
        mock_handle.assert_called_once_with("blog", str(tmp_path))
        assert result == 0


@pytest.mark.unit
def test_legacy_add_notifications(tmp_path: Path):
    with (
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.commands.notifications.handle_add_notifications") as mock_handle,
    ):
        result = _handle_legacy_args(["add-notifications", "--app", "alerts", "--project", "myapp"])
        mock_handle.assert_called_once_with("alerts", str(tmp_path / "src" / "myapp"), arq_dir=None)
        assert result == 0


@pytest.mark.unit
def test_legacy_no_command(capsys):
    result = _handle_legacy_args([])
    assert result == 0
