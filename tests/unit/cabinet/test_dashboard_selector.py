from unittest.mock import MagicMock

import pytest

from codex_django.cabinet.selector.dashboard import DashboardSelector, MetricAdapter, TableAdapter
from codex_django.cabinet.types import MetricWidgetData, TableColumn, TableWidgetData


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
