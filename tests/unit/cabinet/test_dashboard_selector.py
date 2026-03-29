from unittest.mock import MagicMock, patch

import pytest

from codex_django.cabinet.selector.dashboard import DashboardSelector, ListAdapter, MetricAdapter, TableAdapter
from codex_django.cabinet.types import ListItem, ListWidgetData, MetricWidgetData, TableColumn, TableWidgetData

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def clear_providers():
    """Clear registered providers before each test."""
    DashboardSelector._providers = []


def test_selector_extend_with_function():
    @DashboardSelector.extend(cache_key="test_fn", cache_ttl=0)
    def my_provider(request):
        return {"key": "value"}

    context = DashboardSelector.get_context(MagicMock())
    assert context["key"] == "value"


def test_selector_extend_with_adapter():
    def my_metric_provider(request):
        return MetricWidgetData(label="Test", value="100")

    adapter = MetricAdapter(my_metric_provider)
    DashboardSelector.extend(adapter, cache_ttl=0)

    context = DashboardSelector.get_context(MagicMock())
    assert "metric" in context
    assert context["metric"].label == "Test"
    assert context["metric"].value == "100"


def test_selector_extend_as_decorator_with_adapter():
    def my_table_provider(request):
        return TableWidgetData(columns=[TableColumn(key="id", label="ID")], rows=[{"id": 1}])

    class MyTableAdapter(TableAdapter):
        def __init__(self):
            super().__init__(my_table_provider)

    adapter = MyTableAdapter()
    DashboardSelector.extend(adapter, cache_ttl=0)

    context = DashboardSelector.get_context(MagicMock())
    assert "table" in context
    assert context["table"].columns[0].label == "ID"
    assert context["table"].rows[0]["id"] == 1


def test_list_adapter_wraps_provider_payload():
    def my_list_provider(request):
        return ListWidgetData(items=[ListItem(label="A", value="1")], title="Recent")

    adapter = ListAdapter(my_list_provider)

    context = adapter.get_data(MagicMock())

    assert context["list"].title == "Recent"
    assert context["list"].items[0].label == "A"


def test_selector_extend_as_decorator_uses_function_name_as_default_cache_key():
    @DashboardSelector.extend(cache_ttl=60)
    def revenue(request):
        return {"revenue": 120}

    assert DashboardSelector._providers == [{"fn": revenue, "cache_key": "revenue", "cache_ttl": 60}]


def test_selector_extend_with_adapter_uses_lowercased_class_name_as_cache_key():
    def metric_provider(request):
        return MetricWidgetData(label="MRR", value="1200")

    class RevenueAdapter(MetricAdapter):
        def __init__(self):
            super().__init__(metric_provider)

    adapter = RevenueAdapter()

    DashboardSelector.extend(adapter, cache_ttl=45)

    assert DashboardSelector._providers[0]["cache_key"] == "revenueadapter"
    assert DashboardSelector._providers[0]["cache_ttl"] == 45


def test_selector_uses_cached_value_before_calling_provider():
    provider = MagicMock(return_value={"kpi": 10})
    provider.__name__ = "provider"

    DashboardSelector.extend(provider, cache_key="cached_kpi", cache_ttl=300)

    with patch("codex_django.cabinet.selector.dashboard._manager") as manager:
        manager.get.return_value = {"kpi": 99}

        context = DashboardSelector.get_context(MagicMock())

    assert context == {"kpi": 99}
    provider.assert_not_called()
    manager.get.assert_called_once_with("cached_kpi")
    manager.set.assert_not_called()


def test_selector_populates_cache_after_provider_call():
    provider = MagicMock(return_value={"kpi": 10})
    provider.__name__ = "provider"

    DashboardSelector.extend(provider, cache_key="fresh_kpi", cache_ttl=180)

    with patch("codex_django.cabinet.selector.dashboard._manager") as manager:
        manager.get.return_value = None

        context = DashboardSelector.get_context(MagicMock())

    assert context == {"kpi": 10}
    provider.assert_called_once()
    manager.set.assert_called_once_with("fresh_kpi", {"kpi": 10}, ttl=180)


def test_selector_with_zero_cache_ttl_skips_cache_layer():
    provider = MagicMock(return_value={"live": True})
    provider.__name__ = "live_provider"

    DashboardSelector.extend(provider, cache_key="live", cache_ttl=0)

    with patch("codex_django.cabinet.selector.dashboard._manager") as manager:
        context = DashboardSelector.get_context(MagicMock())

    assert context == {"live": True}
    provider.assert_called_once()
    manager.get.assert_not_called()
    manager.set.assert_not_called()


def test_selector_merges_multiple_provider_contexts_in_order():
    first = MagicMock(return_value={"shared": "first", "alpha": 1})
    first.__name__ = "first"
    second = MagicMock(return_value={"shared": "second", "beta": 2})
    second.__name__ = "second"

    DashboardSelector.extend(first, cache_ttl=0)
    DashboardSelector.extend(second, cache_ttl=0)

    context = DashboardSelector.get_context(MagicMock())

    assert context == {"shared": "second", "alpha": 1, "beta": 2}


def test_selector_invalidate_delegates_to_manager():
    with patch("codex_django.cabinet.selector.dashboard._manager") as manager:
        DashboardSelector.invalidate("booking_kpi")

    manager.invalidate.assert_called_once_with("booking_kpi")


def test_selector_invalidate_all_delegates_to_manager():
    with patch("codex_django.cabinet.selector.dashboard._manager") as manager:
        DashboardSelector.invalidate_all()

    manager.invalidate_all.assert_called_once_with()
