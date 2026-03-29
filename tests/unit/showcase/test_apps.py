import pytest

from codex_django.showcase.apps import ShowcaseConfig

pytestmark = pytest.mark.unit


def test_showcase_app_config_metadata():
    assert ShowcaseConfig.name == "codex_django.showcase"
    assert ShowcaseConfig.verbose_name == "Codex Showcase"
