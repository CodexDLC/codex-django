from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from codex_django.core.management.commands.codex_makemessages import Command


@pytest.mark.unit
def test_codex_makemessages_dry_run(settings, tmp_path):
    settings.BASE_DIR = str(tmp_path)
    settings.LANGUAGES = [("en", "English"), ("de", "German")]

    (tmp_path / "templates" / "domain1").mkdir(parents=True)
    (tmp_path / "app1" / "templates").mkdir(parents=True)

    out = StringIO()
    cmd = Command()
    cmd.stdout = out
    cmd.handle(dry_run=True)

    output = out.getvalue()
    assert "Languages: en, de" in output
    assert "Domain: [domain1]" in output
    assert "[DRY-RUN] Executing" in output


@pytest.mark.unit
def test_codex_makemessages_handle_dry_run(settings):
    # Ensure BASE_DIR is present
    settings.BASE_DIR = "."
    with override_settings(LANGUAGES=[("en", "English")]):
        out = StringIO()
        cmd = Command()
        cmd.stdout = out
        cmd.handle(dry_run=True)
        # The command output for domain scan might vary, checking for "Domain:" instead
        assert "Domain:" in out.getvalue()


@pytest.mark.unit
def test_codex_makemessages_no_languages(settings):
    settings.BASE_DIR = "."
    with override_settings(LANGUAGES=[]):
        out = StringIO()
        cmd = Command()
        cmd.stdout = out
        cmd.handle(dry_run=True)
        assert "No LANGUAGES defined" in out.getvalue()


@pytest.mark.unit
def test_codex_makemessages_run_success(settings, tmp_path):
    settings.BASE_DIR = str(tmp_path)
    settings.LANGUAGES = [("en", "English")]
    (tmp_path / "templates" / "domain1").mkdir(parents=True)

    out = StringIO()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        cmd = Command()
        cmd.stdout = out
        cmd.handle(dry_run=False)

    assert "[OK] Updated locale for domain1" in out.getvalue()
