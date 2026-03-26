"""Unit tests for deploy, quality, and utils CLI modules."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_ENGINE_PATH = "codex_django.cli.engine.CLIEngine"


# ---------------------------------------------------------------------------
# deploy.py
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHandleGenerateDeploy:
    # deploy.py imports CLIEngine at module level, so we patch the local name
    _DEPLOY_ENGINE = "codex_django.cli.commands.deploy.CLIEngine"

    def test_scaffolds_deploy_files(self, tmp_path: Path):
        with patch(self._DEPLOY_ENGINE) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django.cli.commands.deploy import handle_generate_deploy

            handle_generate_deploy("myproject", str(tmp_path))

            mock_engine.scaffold.assert_called_once()
            call_kwargs = mock_engine.scaffold.call_args
            assert call_kwargs[0][0] == "deploy"
            assert "myproject" in call_kwargs[1]["target_dir"]
            assert call_kwargs[1]["context"]["project_name"] == "myproject"

    def test_deploy_target_dir_is_inside_deploy_folder(self, tmp_path: Path):
        with patch(self._DEPLOY_ENGINE) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django.cli.commands.deploy import handle_generate_deploy

            handle_generate_deploy("testapp", str(tmp_path))

            target_dir = mock_engine.scaffold.call_args[1]["target_dir"]
            assert "deploy" in target_dir
            assert "testapp" in target_dir


# ---------------------------------------------------------------------------
# quality.py
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHandleConfigurePrecommit:
    def test_creates_precommit_config(self, tmp_path: Path):
        from codex_django.cli.commands.quality import handle_configure_precommit

        handle_configure_precommit(str(tmp_path))

        config = tmp_path / ".pre-commit-config.yaml"
        assert config.exists()
        content = config.read_text(encoding="utf-8")
        assert "ruff" in content
        assert "bandit" in content

    def test_creates_secrets_baseline_if_missing(self, tmp_path: Path):
        from codex_django.cli.commands.quality import handle_configure_precommit

        handle_configure_precommit(str(tmp_path))

        baseline = tmp_path / ".secrets.baseline"
        assert baseline.exists()

    def test_does_not_overwrite_existing_baseline(self, tmp_path: Path):
        import json

        baseline = tmp_path / ".secrets.baseline"
        baseline.write_text(json.dumps({"custom": True}), encoding="utf-8")

        from codex_django.cli.commands.quality import handle_configure_precommit

        handle_configure_precommit(str(tmp_path))

        # Existing baseline should not be overwritten
        content = json.loads(baseline.read_text(encoding="utf-8"))
        assert content.get("custom") is True


# ---------------------------------------------------------------------------
# utils.py
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRunDjangoCommand:
    def test_executes_command_successfully(self):
        with patch("django.core.management.execute_from_command_line") as mock_exec:
            from codex_django.cli.utils import run_django_command

            run_django_command(["migrate"])

            mock_exec.assert_called_once_with(["manage.py", "migrate"])

    def test_handles_system_exit_zero(self):
        with patch(
            "django.core.management.execute_from_command_line",
            side_effect=SystemExit(0),
        ):
            from codex_django.cli.utils import run_django_command

            # Should not raise
            run_django_command(["migrate"])

    def test_handles_system_exit_nonzero(self, capsys):
        with patch(
            "django.core.management.execute_from_command_line",
            side_effect=SystemExit(1),
        ):
            from codex_django.cli.utils import run_django_command

            run_django_command(["migrate"])

            captured = capsys.readouterr()
            assert "failed" in captured.out.lower() or "1" in captured.out

    def test_handles_generic_exception(self, capsys):
        with patch(
            "django.core.management.execute_from_command_line",
            side_effect=RuntimeError("boom"),
        ):
            from codex_django.cli.utils import run_django_command

            run_django_command(["migrate"])

            captured = capsys.readouterr()
            assert "boom" in captured.out
