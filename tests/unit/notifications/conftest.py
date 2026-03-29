from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_i18n_adapter():
    """i18n adapter whose translation_override is a real context manager."""

    @contextmanager
    def _override(lang):
        yield

    adapter = MagicMock()
    adapter.translation_override.side_effect = _override
    return adapter


@pytest.fixture
def mock_cache_adapter():
    """Cache adapter that returns None by default (cache miss)."""
    cache = MagicMock()
    cache.get.return_value = None
    return cache


@pytest.fixture
def mock_model():
    """Model mock with a real DoesNotExist exception class."""
    DoesNotExist = type("DoesNotExist", (Exception,), {})
    model = MagicMock()
    model.DoesNotExist = DoesNotExist
    return model
