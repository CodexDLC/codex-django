import pytest
from unittest.mock import MagicMock, patch
from codex_django.cabinet.context_processors import cabinet
from codex_django.cabinet.registry import CabinetRegistry
from codex_django.cabinet.types import CabinetSection, DashboardWidget


@pytest.fixture
def registry():
    reg = CabinetRegistry()
    # Sections
    reg.register("admin_mod", section=CabinetSection(label="Admin Sec", icon="i", nav_group="admin"))
    reg.register("client_mod", section=CabinetSection(label="Client Sec", icon="i", nav_group="client"))
    # Widgets
    reg.register("admin_mod", dashboard_widget=DashboardWidget(template="a.html", nav_group="admin"))
    reg.register("client_mod", dashboard_widget=DashboardWidget(template="c.html", nav_group="client"))
    return reg


def test_context_processor_no_group(registry):
    request = MagicMock()
    request.user.is_authenticated = True
    request.user.has_perm.return_value = True
    # No cabinet_nav_group attribute
    del request.cabinet_nav_group

    with (
        patch("codex_django.cabinet.context_processors.cabinet_registry", registry),
        patch("codex_django.cabinet.context_processors._settings_manager") as mock_mgr,
    ):
        mock_mgr.get.return_value = None
        result = cabinet(request)

    # Default behavior: get_sections(None) returns all
    assert len(result["cabinet_nav"]) == 2
    assert len(result["cabinet_dashboard_widgets"]) == 2


def test_context_processor_admin_group(registry):
    from django.test import RequestFactory
    factory = RequestFactory()
    request = factory.get("/")
    request.cabinet_nav_group = "admin"
    request.user = MagicMock(is_authenticated=True)
    request.user.has_perm.return_value = True

    with (
        patch("codex_django.cabinet.context_processors.cabinet_registry", registry),
        patch("codex_django.cabinet.context_processors._settings_manager") as mock_mgr,
    ):
        mock_mgr.get.return_value = None
        result = cabinet(request)

    assert len(result["cabinet_nav"]) == 1
    assert result["cabinet_nav"][0].label == "Admin Sec"
    assert len(result["cabinet_dashboard_widgets"]) == 1
    assert result["cabinet_dashboard_widgets"][0].template == "a.html"


def test_context_processor_client_group(registry):
    from django.test import RequestFactory
    factory = RequestFactory()
    request = factory.get("/")
    request.cabinet_nav_group = "client"
    request.user = MagicMock(is_authenticated=True)
    request.user.has_perm.return_value = True

    with (
        patch("codex_django.cabinet.context_processors.cabinet_registry", registry),
        patch("codex_django.cabinet.context_processors._settings_manager") as mock_mgr,
    ):
        mock_mgr.get.return_value = None
        result = cabinet(request)

    assert len(result["cabinet_nav"]) == 1
    assert result["cabinet_nav"][0].label == "Client Sec"
    assert len(result["cabinet_dashboard_widgets"]) == 1
    assert result["cabinet_dashboard_widgets"][0].template == "c.html"
