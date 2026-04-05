import pytest
from codex_django.notifications.registry import NotificationEventRegistry
from codex_django.notifications.contracts import NotificationDispatchSpec

@pytest.mark.unit
def test_registry_register_and_get():
    registry = NotificationEventRegistry()
    @registry.register("test_event")
    def handler():
        return None
    
    handlers = registry.get_handlers("test_event")
    assert len(handlers) == 1
    assert handlers[0] == handler

@pytest.mark.unit
def test_registry_build_specs_single():
    registry = NotificationEventRegistry()
    spec = NotificationDispatchSpec(
        recipient_email="a@b.com",
        subject_key="S",
        event_type="e",
        channels=[],
    )
    
    @registry.register("event")
    def handler(*args, **kwargs):
        return spec
    
    specs = registry.build_specs("event")
    assert specs == [spec]

@pytest.mark.unit
def test_registry_build_specs_list():
    registry = NotificationEventRegistry()
    spec = NotificationDispatchSpec(
        recipient_email="a@b.com",
        subject_key="S",
        event_type="e",
        channels=[],
    )
    
    @registry.register("event")
    def handler(*args, **kwargs):
        return [spec, None]
    
    specs = registry.build_specs("event")
    assert specs == [spec]

@pytest.mark.unit
def test_registry_build_specs_invalid_return_type():
    registry = NotificationEventRegistry()
    @registry.register("event")
    def handler(*args, **kwargs):
        return 123
    
    with pytest.raises(TypeError, match="must return NotificationDispatchSpec"):
        registry.build_specs("event")

@pytest.mark.unit
def test_registry_build_specs_invalid_item_in_list():
    registry = NotificationEventRegistry()
    @registry.register("event")
    def handler(*args, **kwargs):
        return ["not-a-spec"]
    
    with pytest.raises(TypeError, match="returned non-spec item"):
        registry.build_specs("event")
