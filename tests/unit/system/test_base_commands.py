"""
Unit tests for codex_django.system.management.base_commands
============================================================
All Redis/filesystem calls are mocked.
"""

from io import StringIO
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from django.core.management.base import CommandError

from codex_django.system.management.base_commands import (
    BaseHashProtectedCommand,
    BaseUpdateAllContentCommand,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class ConcreteUpdateAll(BaseUpdateAllContentCommand):
    """Minimal concrete subclass with a fixed commands_to_run list."""

    commands_to_run = ["cmd_a", "cmd_b"]


class ConcreteUpdateAllEmpty(BaseUpdateAllContentCommand):
    """Subclass with no commands defined."""

    commands_to_run = []


# ---------------------------------------------------------------------------
# BaseUpdateAllContentCommand
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBaseUpdateAllContentCommand:
    def _make_cmd(self, cls=ConcreteUpdateAll):
        cmd = cls()
        cmd.stdout = StringIO()
        cmd.stderr = StringIO()
        cmd.style = MagicMock()
        cmd.style.WARNING = lambda x: x
        cmd.style.SUCCESS = lambda x: x
        cmd.style.ERROR = lambda x: x
        return cmd

    def test_empty_commands_to_run_prints_warning(self):
        cmd = self._make_cmd(ConcreteUpdateAllEmpty)
        cmd.handle(force=False)
        out = cmd.stdout.getvalue()
        assert "No commands defined" in out

    def test_all_subcommands_succeed(self):
        cmd = self._make_cmd()
        with patch("codex_django.system.management.base_commands.call_command") as mock_call:
            cmd.handle(force=False)
            assert mock_call.call_count == 2
        out = cmd.stdout.getvalue()
        assert "All updates completed" in out

    def test_one_subcommand_fails_raises_command_error(self):
        cmd = self._make_cmd()
        with (
            patch(
                "codex_django.system.management.base_commands.call_command",
                side_effect=Exception("Boom"),
            ),
            pytest.raises(CommandError, match="One or more subcommands failed"),
        ):
            cmd.handle(force=False)

    def test_force_flag_passed_to_subcommands(self):
        cmd = self._make_cmd()
        with patch("codex_django.system.management.base_commands.call_command") as mock_call:
            cmd.handle(force=True)
            for call in mock_call.call_args_list:
                assert call.kwargs.get("force") is True or call.args[1:] == (True,) or call[1].get("force") is True


# ---------------------------------------------------------------------------
# BaseHashProtectedCommand
# ---------------------------------------------------------------------------


class ConcreteHashCmd(BaseHashProtectedCommand):
    """Usable concrete subclass for testing."""

    fixture_key = "test_fixture"
    _fake_paths: list[Path] = []
    _import_result: bool = True

    def get_fixture_paths(self) -> list[Path]:
        return self._fake_paths

    def handle_import(self, *args: Any, **options: Any) -> bool:
        return self._import_result


class ConcreteHashCmdNoKey(BaseHashProtectedCommand):
    """Subclass without fixture_key set."""

    fixture_key = ""

    def get_fixture_paths(self) -> list[Path]:
        return []

    def handle_import(self, *args: Any, **options: Any) -> bool:
        return True


@pytest.mark.unit
class TestBaseHashProtectedCommand:
    def _make_cmd(self, cls=ConcreteHashCmd):
        cmd = cls()
        cmd.stdout = StringIO()
        cmd.style = MagicMock()
        cmd.style.WARNING = lambda x: x
        cmd.style.SUCCESS = lambda x: x
        return cmd

    def test_no_fixture_key_raises_value_error(self):
        cmd = self._make_cmd(ConcreteHashCmdNoKey)
        with pytest.raises(ValueError, match="fixture_key is not set"):
            cmd.handle(force=False)

    def test_no_fixture_files_prints_warning(self, tmp_path):
        cmd = self._make_cmd()
        # _fake_paths is empty by default, so no real files
        with patch("codex_django.system.management.base_commands.get_fixture_hash_manager"):
            cmd.handle(force=False)
        out = cmd.stdout.getvalue()
        assert "Skipped" in out
        assert "No fixtures found" in out

    def test_hash_unchanged_no_force_skips_import(self, tmp_path):
        fixture = tmp_path / "data.json"
        fixture.write_text("{}")

        cmd = self._make_cmd()
        cmd._fake_paths = [fixture]

        mock_manager = MagicMock()
        mock_manager.get_hash.return_value = "abc123"

        with (
            patch("codex_django.system.management.base_commands.get_fixture_hash_manager", return_value=mock_manager),
            patch(
                "codex_django.system.management.base_commands.compute_paths_hash",
                return_value="abc123",
            ),
        ):
            cmd.handle(force=False)

        out = cmd.stdout.getvalue()
        assert "Skipped" in out
        assert "fixture hash unchanged" in out
        mock_manager.set_hash.assert_not_called()

    def test_hash_changed_calls_import_and_updates_hash(self, tmp_path):
        fixture = tmp_path / "data.json"
        fixture.write_text("{}")

        cmd = self._make_cmd()
        cmd._fake_paths = [fixture]

        mock_manager = MagicMock()
        mock_manager.get_hash.return_value = "old_hash"

        with (
            patch("codex_django.system.management.base_commands.get_fixture_hash_manager", return_value=mock_manager),
            patch(
                "codex_django.system.management.base_commands.compute_paths_hash",
                return_value="new_hash",
            ),
        ):
            cmd.handle(force=False)

        mock_manager.set_hash.assert_called_once_with("test_fixture", "new_hash")

    def test_force_true_ignores_hash_and_calls_import(self, tmp_path):
        fixture = tmp_path / "data.json"
        fixture.write_text("{}")

        cmd = self._make_cmd()
        cmd._fake_paths = [fixture]

        mock_manager = MagicMock()
        mock_manager.get_hash.return_value = "same_hash"

        with (
            patch("codex_django.system.management.base_commands.get_fixture_hash_manager", return_value=mock_manager),
            patch(
                "codex_django.system.management.base_commands.compute_paths_hash",
                return_value="same_hash",
            ),
        ):
            cmd.handle(force=True)

        # Even though hashes match, force=True should call set_hash
        mock_manager.set_hash.assert_called_once()
