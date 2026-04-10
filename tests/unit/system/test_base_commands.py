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
    JsonFixtureUpsertCommand,
    SingletonFixtureUpdateCommand,
    load_json_fixture_rows,
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


class ConcreteUpdateAllWithHooks(BaseUpdateAllContentCommand):
    """Subclass that records aggregate command hooks."""

    commands_to_run = ["cmd_a", "cmd_b"]

    def __init__(self):
        super().__init__()
        self.events: list[str] = []

    def get_command_label(self, command_name: str) -> str:
        self.events.append(f"label:{command_name}")
        return command_name.upper()

    def before_subcommand(self, command_name: str) -> None:
        self.events.append(f"before:{command_name}")

    def after_subcommand(self, command_name: str) -> None:
        self.events.append(f"after:{command_name}")


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

    def test_subcommand_hooks_are_called_in_order(self):
        cmd = self._make_cmd(ConcreteUpdateAllWithHooks)
        with patch("codex_django.system.management.base_commands.call_command"):
            cmd.handle(force=False)

        assert cmd.events == [
            "label:cmd_a",
            "before:cmd_a",
            "after:cmd_a",
            "label:cmd_b",
            "before:cmd_b",
            "after:cmd_b",
        ]


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


# ---------------------------------------------------------------------------
# JSON fixture helpers and commands
# ---------------------------------------------------------------------------


class FakeUpsertModel:
    objects = MagicMock()


class ConcreteJsonUpsertCmd(JsonFixtureUpsertCommand):
    fixture_key = "json_fixture"
    model_class = FakeUpsertModel
    lookup_field = "key"


class FakeSingleton:
    def __init__(self) -> None:
        self.phone = "old"
        self.email = "same"
        self.saved = False

    def save(self) -> None:
        self.saved = True


class FakeSingletonModel:
    instance = FakeSingleton()

    @classmethod
    def load(cls) -> FakeSingleton:
        return cls.instance


class ConcreteSingletonCmd(SingletonFixtureUpdateCommand):
    fixture_key = "site_settings"
    model_class = FakeSingletonModel

    def __init__(self):
        super().__init__()
        self.synced_instance = None

    def sync_instance(self, instance: Any) -> None:
        self.synced_instance = instance


@pytest.mark.unit
class TestJsonFixtureHelpers:
    def test_load_json_fixture_rows_returns_fields(self, tmp_path):
        fixture = tmp_path / "data.json"
        fixture.write_text('[{"fields": {"key": "hero", "content": "Welcome"}}]', encoding="utf-8")

        result = load_json_fixture_rows(fixture)

        assert result.success is True
        assert result.rows == [{"key": "hero", "content": "Welcome"}]
        assert result.skipped == 0

    def test_load_json_fixture_rows_reports_invalid_json(self, tmp_path):
        fixture = tmp_path / "data.json"
        fixture.write_text("{", encoding="utf-8")

        result = load_json_fixture_rows(fixture)

        assert result.success is False
        assert "Error decoding JSON fixture" in result.errors[0]

    def test_load_json_fixture_rows_rejects_non_list_payload(self, tmp_path):
        fixture = tmp_path / "data.json"
        fixture.write_text('{"fields": {"key": "hero"}}', encoding="utf-8")

        result = load_json_fixture_rows(fixture)

        assert result.success is False
        assert "expected a list" in result.errors[0]

    def test_load_json_fixture_rows_skips_items_without_fields(self, tmp_path):
        fixture = tmp_path / "data.json"
        fixture.write_text('[{"fields": {"key": "hero"}}, {"pk": 1}, 42]', encoding="utf-8")

        result = load_json_fixture_rows(fixture)

        assert result.success is True
        assert result.rows == [{"key": "hero"}]
        assert result.skipped == 2


@pytest.mark.unit
class TestJsonFixtureUpsertCommand:
    def _make_cmd(self, fixture: Path):
        cmd = ConcreteJsonUpsertCmd()
        cmd.fixture_path = fixture
        cmd.stdout = StringIO()
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda x: x
        cmd.style.ERROR = lambda x: x
        return cmd

    def test_upsert_creates_updates_and_skips_missing_lookup(self, tmp_path):
        fixture = tmp_path / "data.json"
        fixture.write_text(
            """[
                {"fields": {"key": "hero", "content": "Welcome"}},
                {"fields": {"key": "cta", "content": "Book"}},
                {"fields": {"content": "Missing key"}}
            ]""",
            encoding="utf-8",
        )
        FakeUpsertModel.objects = MagicMock()
        FakeUpsertModel.objects.update_or_create.side_effect = [
            (MagicMock(), True),
            (MagicMock(), False),
        ]
        cmd = self._make_cmd(fixture)

        with (
            patch("codex_django.system.management.base_commands.get_fixture_hash_manager") as mock_hash_factory,
            patch("codex_django.system.management.base_commands.compute_paths_hash", return_value="new_hash"),
        ):
            mock_hash = mock_hash_factory.return_value
            mock_hash.get_hash.return_value = "old_hash"
            cmd.handle(force=False)

        assert FakeUpsertModel.objects.update_or_create.call_count == 2
        FakeUpsertModel.objects.update_or_create.assert_any_call(
            key="hero",
            defaults={"key": "hero", "content": "Welcome"},
        )
        assert cmd.import_result.created == 1
        assert cmd.import_result.updated == 1
        assert cmd.import_result.skipped == 1
        mock_hash.set_hash.assert_called_once_with("json_fixture", "new_hash")

    def test_invalid_json_returns_false_and_does_not_update_hash(self, tmp_path):
        fixture = tmp_path / "data.json"
        fixture.write_text("{", encoding="utf-8")
        FakeUpsertModel.objects = MagicMock()
        cmd = self._make_cmd(fixture)

        with (
            patch("codex_django.system.management.base_commands.get_fixture_hash_manager") as mock_hash_factory,
            patch("codex_django.system.management.base_commands.compute_paths_hash", return_value="new_hash"),
        ):
            mock_hash = mock_hash_factory.return_value
            mock_hash.get_hash.return_value = "old_hash"
            cmd.handle(force=False)

        FakeUpsertModel.objects.update_or_create.assert_not_called()
        mock_hash.set_hash.assert_not_called()
        assert "Error decoding JSON fixture" in cmd.stdout.getvalue()

    def test_force_true_imports_when_hash_unchanged(self, tmp_path):
        fixture = tmp_path / "data.json"
        fixture.write_text('[{"fields": {"key": "hero"}}]', encoding="utf-8")
        FakeUpsertModel.objects = MagicMock()
        FakeUpsertModel.objects.update_or_create.return_value = (MagicMock(), True)
        cmd = self._make_cmd(fixture)

        with (
            patch("codex_django.system.management.base_commands.get_fixture_hash_manager") as mock_hash_factory,
            patch("codex_django.system.management.base_commands.compute_paths_hash", return_value="same_hash"),
        ):
            mock_hash = mock_hash_factory.return_value
            mock_hash.get_hash.return_value = "same_hash"
            cmd.handle(force=True)

        FakeUpsertModel.objects.update_or_create.assert_called_once()
        mock_hash.set_hash.assert_called_once_with("json_fixture", "same_hash")


@pytest.mark.unit
class TestSingletonFixtureUpdateCommand:
    def _make_cmd(self, fixture: Path):
        cmd = ConcreteSingletonCmd()
        cmd.fixture_path = fixture
        cmd.stdout = StringIO()
        cmd.style = MagicMock()
        cmd.style.WARNING = lambda x: x
        cmd.style.SUCCESS = lambda x: x
        cmd.style.ERROR = lambda x: x
        return cmd

    def test_updates_changed_fields_and_syncs(self, tmp_path):
        fixture = tmp_path / "settings.json"
        fixture.write_text('[{"fields": {"phone": "new", "email": "same", "unknown": "ignored"}}]', encoding="utf-8")
        FakeSingletonModel.instance = FakeSingleton()
        cmd = self._make_cmd(fixture)

        with (
            patch("codex_django.system.management.base_commands.get_fixture_hash_manager") as mock_hash_factory,
            patch("codex_django.system.management.base_commands.compute_paths_hash", return_value="new_hash"),
        ):
            mock_hash = mock_hash_factory.return_value
            mock_hash.get_hash.return_value = "old_hash"
            cmd.handle(force=False)

        assert FakeSingletonModel.instance.phone == "new"
        assert FakeSingletonModel.instance.saved is True
        assert cmd.synced_instance is FakeSingletonModel.instance
        assert cmd.updated_fields == ["phone"]
        mock_hash.set_hash.assert_called_once_with("site_settings", "new_hash")

    def test_unchanged_singleton_does_not_save_or_sync(self, tmp_path):
        fixture = tmp_path / "settings.json"
        fixture.write_text('[{"fields": {"phone": "old", "email": "same"}}]', encoding="utf-8")
        FakeSingletonModel.instance = FakeSingleton()
        cmd = self._make_cmd(fixture)

        with (
            patch("codex_django.system.management.base_commands.get_fixture_hash_manager") as mock_hash_factory,
            patch("codex_django.system.management.base_commands.compute_paths_hash", return_value="new_hash"),
        ):
            mock_hash = mock_hash_factory.return_value
            mock_hash.get_hash.return_value = "old_hash"
            cmd.handle(force=False)

        assert FakeSingletonModel.instance.saved is False
        assert cmd.synced_instance is None
        assert cmd.updated_fields == []
        mock_hash.set_hash.assert_called_once_with("site_settings", "new_hash")

    def test_missing_fixture_is_skipped_by_hash_base(self):
        missing = Path("missing-settings.json")
        cmd = self._make_cmd(missing)

        with patch("codex_django.system.management.base_commands.get_fixture_hash_manager"):
            cmd.handle(force=False)

        assert "No fixtures found" in cmd.stdout.getvalue()
