from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from django.contrib.staticfiles import finders
from django.template.loader import get_template, render_to_string
from django.test import override_settings

from codex_django.cabinet.templatetags.cabinet_tags import (
    cab_initials,
    cab_trans,
    cab_url,
    get_item,
    jsonify,
    optional_static_css,
    sidebar_badge,
)


@pytest.mark.unit
def test_get_item():
    assert get_item({"a": 1}, "a") == 1
    assert get_item({"a": 1}, "b") == ""
    assert get_item(None, "a") == ""


@pytest.mark.unit
def test_cab_initials():
    user = MagicMock()
    user.first_name = "Ivan"
    user.last_name = "Petrov"
    assert cab_initials(user) == "IP"

    user.first_name = ""
    user.last_name = ""
    user.username = "admin"
    assert cab_initials(user) == "AD"


@pytest.mark.unit
def test_cab_trans():
    # Simple test without setting up i18n
    assert cab_trans("Hello") == "Hello"


@pytest.mark.unit
def test_cab_url():
    # Defensive reversal test
    assert cab_url("nonexistent") == "#"


@pytest.mark.unit
def test_optional_static_css_returns_empty_when_asset_is_missing(monkeypatch):
    monkeypatch.setattr(finders, "find", lambda path: None)

    assert optional_static_css("cabinet/css/app_cabinet.css") == ""


@pytest.mark.unit
@override_settings(STATIC_URL="/static/")
def test_optional_static_css_renders_link_when_asset_exists(monkeypatch):
    monkeypatch.setattr(finders, "find", lambda path: "/tmp/app_cabinet.css")

    assert (
        optional_static_css("cabinet/css/app_cabinet.css")
        == '<link rel="stylesheet" href="/static/cabinet/css/app_cabinet.css">'
    )


@pytest.mark.unit
@override_settings(STATIC_URL="/static/")
def test_cabinet_head_loads_optional_app_cabinet_after_library_css(monkeypatch):
    monkeypatch.setattr(finders, "find", lambda path: "/tmp/app_cabinet.css")

    html = render_to_string("cabinet/includes/_head.html")

    codex_index = html.index("cabinet/css/codex_cabinet.css")
    app_index = html.index("cabinet/css/app_cabinet.css")
    assert codex_index < app_index


@pytest.mark.unit
def test_sidebar_badge():
    ctx = {"unread": 5}
    assert sidebar_badge(ctx, "unread") == "5"
    assert sidebar_badge(ctx, "") == ""
    assert sidebar_badge(ctx, "missing") == ""


@pytest.mark.unit
def test_jsonify():
    from dataclasses import dataclass

    @dataclass
    class D:
        a: int

    assert '{"a": 1}' in jsonify(D(a=1))


@pytest.mark.unit
@pytest.mark.parametrize(
    "template_name",
    [
        "cabinet/widgets/chart.html",
        "cabinet/widgets/donut.html",
        "cabinet/reports/chart.html",
        "cabinet/widgets/table.html",
        "cabinet/includes/_report_filters.html",
    ],
)
def test_cabinet_templates_load_registered_tag_library(template_name):
    assert get_template(template_name)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("template_name", "component_name", "context"),
    [
        (
            "cabinet/widgets/chart.html",
            "chartWidget",
            {
                "data": {
                    "chart_id": "appointmentsChart",
                    "title": "Appointments",
                    "chart_labels": ["Mon", "Tue"],
                    "chart_data": [4, 7],
                }
            },
        ),
        (
            "cabinet/widgets/donut.html",
            "donutWidget",
            {
                "data": {
                    "chart_id": "categoriesDonut",
                    "title": "Popular categories",
                    "icon": "bi-pie-chart-fill",
                    "chart_labels": ["Nails", "Brows"],
                    "chart_data": [18, 16],
                    "colors": ["#10b981", "#34d399"],
                }
            },
        ),
        (
            "cabinet/reports/chart.html",
            "chartWidget",
            {
                "chart": SimpleNamespace(
                    as_widget_config={
                        "chart_id": "revenueChart",
                        "title": "Revenue",
                        "chart_labels": ["Mon", "Tue"],
                        "chart_data": [100, 120],
                    },
                    description="",
                    height="260px",
                    icon="bi-graph-up-arrow",
                    title="Revenue",
                )
            },
        ),
    ],
)
def test_chart_templates_pass_json_object_to_x_data(template_name, component_name, context):
    html = render_to_string(
        template_name,
        context,
    )

    assert f'x-data=\'{component_name}({{"chart_id":' in html
    assert "force_escape" not in html
    assert "&quot;" not in html
