import importlib
import warnings

import pytest

from codex_django.messaging.registry import messaging_event_registry
from codex_django.messaging.service import BaseMessagingEngine
from codex_django.notifications.registry import notification_event_registry
from codex_django.notifications.service import BaseNotificationEngine

pytestmark = pytest.mark.unit


def test_notifications_package_warns_on_package_level_symbol_access():
    module = importlib.import_module("codex_django.notifications")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        value = module.BaseNotificationEngine

    assert value is BaseMessagingEngine
    assert any(item.category is DeprecationWarning for item in caught)


def test_notifications_submodule_engine_aliases_messaging_engine():
    assert BaseNotificationEngine is BaseMessagingEngine


def test_notifications_and_messaging_share_the_same_registry_object():
    assert notification_event_registry is messaging_event_registry
