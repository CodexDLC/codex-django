import pytest
from django.apps import AppConfig
from codex_django.core.apps import CoreConfig

@pytest.mark.unit
def test_core_config():
    assert CoreConfig.name == "codex_django.core"
    assert issubclass(CoreConfig, AppConfig)
    
    config = CoreConfig("codex_django.core", __import__("codex_django.core"))
    assert config.name == "codex_django.core"
