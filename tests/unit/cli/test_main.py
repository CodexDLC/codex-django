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
    # Inside a project: _project_menu is used; "❌  Exit" returns 0
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="❌  Exit"),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_none_action():
    # Inside a project: None from ask_project_action → returns 0
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value=None),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_init(tmp_path: Path):
    # Outside a project: global menu → init wizard → standard mode
    with (
        patch("codex_django.cli.main._is_in_project", return_value=False),
        patch.object(prompts_module, "ask_main_action", return_value="🚀  Init new project"),
        patch.object(prompts_module, "ask_project_name", return_value="myproject"),
        patch.object(prompts_module, "ask_init_mode", return_value="⚡  Standard"),
        patch.object(prompts_module, "ask_multilingual", return_value=False),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.commands.init.handle_init") as mock_handle,
    ):
        result = _interactive_menu()
        mock_handle.assert_called_once_with(
            "myproject",
            str(tmp_path),
            overwrite=False,
            multilingual=False,
            with_cabinet=False,
            with_booking=False,
            with_notifications=False,
        )
        assert result == 0


@pytest.mark.unit
def test_interactive_menu_init_empty_name():
    # Outside a project: project name prompt returns None → exits cleanly
    with (
        patch("codex_django.cli.main._is_in_project", return_value=False),
        patch.object(prompts_module, "ask_main_action", return_value="🚀  Init new project"),
        patch.object(prompts_module, "ask_project_name", return_value=None),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_add_feature_no_pyproject(tmp_path: Path):
    # Inside a project but src/ has no sub-projects → _handle_scaffolding returns 1
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🧩  Scaffolding (Apps/Modules)"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.listdir", return_value=[]),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
    ):
        assert _interactive_menu() == 1


@pytest.mark.unit
def test_interactive_menu_add_app(tmp_path: Path):
    src = tmp_path / "src" / "myproject"
    src.mkdir(parents=True)

    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🧩  Scaffolding (Apps/Modules)"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
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
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🧩  Scaffolding (Apps/Modules)"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
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
def test_interactive_menu_client_cabinet(tmp_path: Path):
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🧩  Scaffolding (Apps/Modules)"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch.object(prompts_module, "ask_target_project", return_value="myproject"),
        patch.object(prompts_module, "ask_feature", return_value="Client Cabinet"),
        patch("codex_django.cli.commands.client_cabinet.handle_add_client_cabinet") as mock_handle,
    ):
        result = _interactive_menu()
        mock_handle.assert_called_once()
        assert result == 0


@pytest.mark.unit
def test_interactive_menu_back_from_feature():
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🧩  Scaffolding (Apps/Modules)"),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch.object(prompts_module, "ask_target_project", return_value="myproject"),
        patch.object(prompts_module, "ask_feature", return_value="← Back"),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_no_src_dir(tmp_path: Path):
    # src/ has no project subdirectories (isdir filter makes everything disappear) → returns 1
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🧩  Scaffolding (Apps/Modules)"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.listdir", return_value=[]),
        patch("codex_django.cli.main.os.path.isdir", return_value=False),
    ):
        assert _interactive_menu() == 1


@pytest.mark.unit
def test_interactive_menu_empty_src_dir(tmp_path: Path):
    # src/ exists but has no projects — listdir returns empty list
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🧩  Scaffolding (Apps/Modules)"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=[]),
    ):
        assert _interactive_menu() == 1


@pytest.mark.unit
def test_interactive_menu_target_project_none(tmp_path: Path):
    # ask_target_project returns None (user pressed Ctrl+C) → returns 0
    # Need multiple projects so the selection prompt is actually shown
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🧩  Scaffolding (Apps/Modules)"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["project_a", "project_b"]),
        patch.object(prompts_module, "ask_target_project", return_value=None),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_basic_app_empty_name(tmp_path: Path):
    # ask_app_name returns None for "Basic app" → returns 0
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🧩  Scaffolding (Apps/Modules)"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch.object(prompts_module, "ask_target_project", return_value="myproject"),
        patch.object(prompts_module, "ask_feature", return_value="Basic app"),
        patch.object(prompts_module, "ask_app_name", return_value=None),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_notifications_empty_name(tmp_path: Path):
    # ask_app_name returns None for "Notifications" → returns 0
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🧩  Scaffolding (Apps/Modules)"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch.object(prompts_module, "ask_target_project", return_value="myproject"),
        patch.object(prompts_module, "ask_feature", return_value="Notifications"),
        patch.object(prompts_module, "ask_app_name", return_value=None),
    ):
        assert _interactive_menu() == 0


# ---------------------------------------------------------------------------
# main() — "menu" subcommand
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_main_menu_subcommand_no_extra_args():
    # "menu" with no trailing args → calls _interactive_menu
    with patch("codex_django.cli.main._interactive_menu", return_value=0) as mock_menu:
        result = main(["menu"])
        mock_menu.assert_called_once()
        assert result == 0


# ---------------------------------------------------------------------------
# _project_menu() — extra branches
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_project_menu_standard_commands_back():
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🚀  Standard Commands"),
        patch.object(prompts_module, "ask_standard_command", return_value="← Back"),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_project_menu_standard_commands_migrate():
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🚀  Standard Commands"),
        patch.object(prompts_module, "ask_standard_command", return_value="migrate"),
        patch("codex_django.cli.utils.run_django_command") as mock_cmd,
    ):
        result = _interactive_menu()
        mock_cmd.assert_called_once_with(["migrate"])
        assert result == 0


@pytest.mark.unit
def test_project_menu_quality_tools_back():
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🛡  Quality & Tools"),
        patch.object(prompts_module, "ask_quality_tool", return_value="← Back"),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_project_menu_quality_configure_precommit():
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🛡  Quality & Tools"),
        patch.object(prompts_module, "ask_quality_tool", return_value="Configure pre-commit"),
        patch("codex_django.cli.main.os.getcwd", return_value="/fake"),
        patch("codex_django.cli.commands.quality.handle_configure_precommit") as mock_quality,
    ):
        result = _interactive_menu()
        mock_quality.assert_called_once_with("/fake")
        assert result == 0


@pytest.mark.unit
def test_project_menu_security_generates_key(capsys):
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="⚙️  Security"),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_project_menu_deployment_back():
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🏁  Deployment Setup"),
        patch.object(prompts_module, "ask_deploy_option", return_value="← Back"),
    ):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_project_menu_deployment_generate_docker(tmp_path: Path):
    with (
        patch("codex_django.cli.main._is_in_project", return_value=True),
        patch.object(prompts_module, "ask_project_action", return_value="🏁  Deployment Setup"),
        patch.object(prompts_module, "ask_deploy_option", return_value="Generate Docker files"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch("codex_django.cli.commands.deploy.handle_generate_deploy") as mock_deploy,
    ):
        result = _interactive_menu()
        mock_deploy.assert_called_once()
        assert result == 0


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
        mock_handle.assert_called_once_with(
            name="myproject",
            base_dir=str(tmp_path),
            target_dir=None,
            code_only=False,
            dev_mode=False,
            overwrite=False,
            multilingual=False,
            with_cabinet=False,
            with_booking=False,
            with_notifications=False,
        )
        assert result == 0


@pytest.mark.unit
def test_legacy_init_multilingual(tmp_path: Path):
    with (
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.commands.init.handle_init") as mock_handle,
    ):
        result = _handle_legacy_args(["init", "myproject", "--multilingual"])
        mock_handle.assert_called_once_with(
            name="myproject",
            base_dir=str(tmp_path),
            target_dir=None,
            code_only=False,
            dev_mode=False,
            overwrite=False,
            multilingual=True,
            with_cabinet=False,
            with_booking=False,
            with_notifications=False,
        )
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
def test_legacy_add_client_cabinet(tmp_path: Path):
    with (
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.commands.client_cabinet.handle_add_client_cabinet") as mock_handle,
    ):
        result = _handle_legacy_args(["add-client-cabinet", "--project", "myapp"])
        mock_handle.assert_called_once_with(str(tmp_path / "src" / "myapp"))
        assert result == 0


@pytest.mark.unit
def test_legacy_no_command(capsys):
    result = _handle_legacy_args([])
    assert result == 0


@pytest.mark.unit
def test_is_in_project():
    from codex_django.cli.main import _is_in_project

    with (
        patch("codex_django.cli.main.os.path.exists", return_value=True),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["myproject"]),
        patch("codex_django.cli.main.os.path.isfile", return_value=True),
    ):
        assert _is_in_project() is True


@pytest.mark.unit
def test_is_in_project_false_when_no_manage_py():
    from codex_django.cli.main import _is_in_project

    # Simulates the library's own source tree: has pyproject.toml + src/ but no manage.py
    with (
        patch("codex_django.cli.main.os.path.exists", return_value=True),
        patch("codex_django.cli.main.os.path.isdir", return_value=True),
        patch("codex_django.cli.main.os.listdir", return_value=["codex_django"]),
        patch("codex_django.cli.main.os.path.isfile", return_value=False),
    ):
        assert _is_in_project() is False


@pytest.mark.unit
def test_is_in_project_false_when_no_pyproject():
    from codex_django.cli.main import _is_in_project

    with patch("codex_django.cli.main.os.path.exists", return_value=False):
        assert _is_in_project() is False


@pytest.mark.unit
@pytest.mark.parametrize(
    "cmd_prompt, expected_arg",
    [
        ("makemigrations", ["makemigrations"]),
        ("createsuperuser", ["createsuperuser"]),
        ("shell", ["shell"]),
        ("i18n: Generate", ["makemessages", "-a"]),
        ("i18n: Compile", ["compilemessages"]),
    ],
)
def test_handle_standard_commands(cmd_prompt, expected_arg):
    from codex_django.cli.main import _handle_standard_commands

    with (
        patch.object(prompts_module, "ask_standard_command", return_value=cmd_prompt),
        patch("codex_django.cli.utils.run_django_command") as mock_cmd,
    ):
        result = _handle_standard_commands()
        mock_cmd.assert_called_once_with(expected_arg)
        assert result == 0


@pytest.mark.unit
def test_handle_scaffolding_forced_project(tmp_path: Path):
    from codex_django.cli.main import _handle_scaffolding

    with (
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch.object(prompts_module, "ask_feature", return_value="Basic app"),
        patch.object(prompts_module, "ask_app_name", return_value="blog"),
        patch("codex_django.cli.commands.add_app.handle_add_app") as mock_handle,
    ):
        result = _handle_scaffolding(forced_project="custom_proj")
        mock_handle.assert_called_once()
        assert result == 0


@pytest.mark.unit
def test_handle_deployment_setup_forced_project(tmp_path: Path):
    from codex_django.cli.main import _handle_deployment_setup

    with (
        patch.object(prompts_module, "ask_deploy_option", return_value="Generate Docker files"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.commands.deploy.handle_generate_deploy") as mock_deploy,
    ):
        result = _handle_deployment_setup(forced_project="custom_proj")
        mock_deploy.assert_called_once_with("custom_proj", str(tmp_path))
        assert result == 0


@pytest.mark.unit
def test_handle_deployment_setup_no_projects(tmp_path: Path):
    from codex_django.cli.main import _handle_deployment_setup

    with (
        patch.object(prompts_module, "ask_deploy_option", return_value="Generate Docker files"),
        patch("codex_django.cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django.cli.main.os.listdir", return_value=[]),
    ):
        result = _handle_deployment_setup()
        assert result == 0


@pytest.mark.unit
def test_handle_quality_tools_project_checker():
    from codex_django.cli.main import _handle_quality_tools

    with (
        patch.object(prompts_module, "ask_quality_tool", return_value="Run Project Checker"),
        patch("subprocess.run") as mock_run,
    ):
        result = _handle_quality_tools()
        mock_run.assert_called_once()
        assert result == 0
