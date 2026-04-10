from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from codex_django.tracking.views import tracking_analytics_view

pytestmark = pytest.mark.unit


def test_tracking_analytics_view_sets_cabinet_module_and_renders_context():
    request = RequestFactory().get("/cabinet/tracking/")
    request.user = SimpleNamespace(is_active=True, is_staff=True, is_superuser=False, is_authenticated=True)

    with (
        patch("codex_django.tracking.views.TrackingSelector.get_analytics_context") as get_context,
        patch("codex_django.tracking.views.render", return_value=HttpResponse("ok")) as render,
    ):
        get_context.return_value.as_dict.return_value = {"tracking_total_views": object()}
        response = tracking_analytics_view(request)

    assert response.status_code == 200
    assert request.cabinet_module == "tracking"
    assert request.cabinet_nav_group == "admin"
    render.assert_called_once_with(
        request,
        "tracking/cabinet/analytics.html",
        {"tracking_total_views": get_context.return_value.as_dict.return_value["tracking_total_views"]},
    )
