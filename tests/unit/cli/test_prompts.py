"""Unit tests for CLI prompt wrappers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestPromptWrappers:
    """Verify that each prompt function delegates to questionary and returns its result."""

    def _make_select(self, return_value):
        """Helper: creates a mock for questionary.select(...).ask() → return_value."""
        mock_q = MagicMock()
        mock_q.ask.return_value = return_value
        return mock_q

    def _make_text(self, return_value):
        mock_q = MagicMock()
        mock_q.ask.return_value = return_value
        return mock_q

    def test_ask_main_action_returns_selection(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("🚀  Init new project")
            result = prompts.ask_main_action()
            assert result == "🚀  Init new project"
            mock_q.select.assert_called_once()

    def test_ask_project_action_returns_selection(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("❌  Exit")
            result = prompts.ask_project_action()
            assert result == "❌  Exit"

    def test_ask_standard_command_returns_selection(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("migrate")
            result = prompts.ask_standard_command()
            assert result == "migrate"

    def test_ask_quality_tool_returns_selection(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("Configure pre-commit")
            result = prompts.ask_quality_tool()
            assert result == "Configure pre-commit"

    def test_ask_deploy_option_returns_selection(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("Generate Docker files")
            result = prompts.ask_deploy_option()
            assert result == "Generate Docker files"

    def test_ask_project_name_returns_text(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.text.return_value = self._make_text("myproject")
            result = prompts.ask_project_name()
            assert result == "myproject"

    def test_ask_target_project_returns_selection(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("myproject")
            result = prompts.ask_target_project(["myproject", "other"])
            assert result == "myproject"

    def test_ask_feature_returns_selection(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("Basic app")
            result = prompts.ask_feature()
            assert result == "Basic app"

    def test_ask_app_name_returns_text(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.text.return_value = self._make_text("blog")
            result = prompts.ask_app_name()
            assert result == "blog"

    def test_ask_app_name_with_default(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.text.return_value = self._make_text("system")
            result = prompts.ask_app_name(default="system")
            assert result == "system"
            _, kwargs = mock_q.text.call_args
            assert kwargs.get("default") == "system"

    def test_ask_multilingual(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.confirm.return_value = self._make_select(True)
            result = prompts.ask_multilingual()
            assert result is True

    def test_ask_languages_single(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("en")
            result = prompts.ask_languages(multilingual=False)
            assert result == ["en"]

    def test_ask_languages_multi(self):
        from codex_django.cli import prompts

        with patch("codex_django.cli.prompts.questionary") as mock_q:
            mock_q.checkbox.return_value = self._make_select(["en", "ru"])
            result = prompts.ask_languages(multilingual=True)
            assert result == ["en", "ru"]
