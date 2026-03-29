import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import codex_django.cli as cli_package
from codex_django.cli._compat import load_cli_module, raise_cli_dependency_error


@pytest.mark.unit
def test_package_main_dispatches_to_split_cli():
    fake_main = MagicMock(return_value=7)
    fake_module = SimpleNamespace(main=fake_main)

    with patch("codex_django.cli.load_cli_module", return_value=fake_module) as mock_loader:
        result = cli_package.main("--help")

    assert result == 7
    mock_loader.assert_called_once_with("main")
    fake_main.assert_called_once_with("--help")


@pytest.mark.unit
def test_raise_cli_dependency_error_rewords_split_package_message():
    exc = ModuleNotFoundError("missing")
    exc.name = "codex_django_cli.main"

    with pytest.raises(ModuleNotFoundError, match="codex-django-cli"):
        raise_cli_dependency_error(exc)


@pytest.mark.unit
def test_raise_cli_dependency_error_reraises_unrelated_module_error():
    exc = ModuleNotFoundError("missing")
    exc.name = "redis"

    with pytest.raises(ModuleNotFoundError) as err:
        raise_cli_dependency_error(exc)

    assert err.value is exc


@pytest.mark.unit
def test_load_cli_module_delegates_to_import_module():
    fake_module = ModuleType("codex_django_cli.main")

    with patch("codex_django.cli._compat.import_module", return_value=fake_module) as mock_import:
        result = load_cli_module("main")

    assert result is fake_module
    mock_import.assert_called_once_with("codex_django_cli.main")


def _execute_shim(module_name: str, relative_path: str) -> ModuleType:
    module_path = Path(__file__).resolve().parents[3] / "src" / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.unit
@pytest.mark.parametrize(
    ("module_name", "target", "relative_path"),
    [
        ("codex_django.cli.main", "main", "codex_django/cli/main.py"),
        ("codex_django.cli.engine", "engine", "codex_django/cli/engine.py"),
        ("codex_django.cli.prompts", "prompts", "codex_django/cli/prompts.py"),
        ("codex_django.cli.utils", "utils", "codex_django/cli/utils.py"),
        ("codex_django.cli.commands", "commands", "codex_django/cli/commands/__init__.py"),
        ("codex_django.cli.commands.add_app", "commands.add_app", "codex_django/cli/commands/add_app.py"),
        ("codex_django.cli.commands.booking", "commands.booking", "codex_django/cli/commands/booking.py"),
        (
            "codex_django.cli.commands.client_cabinet",
            "commands.client_cabinet",
            "codex_django/cli/commands/client_cabinet.py",
        ),
        ("codex_django.cli.commands.deploy", "commands.deploy", "codex_django/cli/commands/deploy.py"),
        ("codex_django.cli.commands.init", "commands.init", "codex_django/cli/commands/init.py"),
        (
            "codex_django.cli.commands.notifications",
            "commands.notifications",
            "codex_django/cli/commands/notifications.py",
        ),
        ("codex_django.cli.commands.quality", "commands.quality", "codex_django/cli/commands/quality.py"),
    ],
)
def test_shim_modules_swap_themselves_with_split_cli_modules(module_name: str, target: str, relative_path: str):
    fake_module = ModuleType(module_name)

    with patch("codex_django.cli._compat.import_module", return_value=fake_module) as mock_import:
        sys.modules.pop(module_name, None)
        module = _execute_shim(module_name, relative_path)

    assert sys.modules[module_name] is fake_module
    assert module is not fake_module
    mock_import.assert_called_once_with(f"codex_django_cli.{target}")
    sys.modules.pop(module_name, None)
