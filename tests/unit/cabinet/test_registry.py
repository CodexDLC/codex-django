"""Unit tests for CabinetRegistry and declare()."""

from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured

from codex_django.cabinet.registry import CabinetRegistry, declare
from codex_django.cabinet.types import CabinetSection, DashboardWidget, NavAction


@pytest.mark.unit
class TestCabinetRegistry:
    def setup_method(self):
        self.registry = CabinetRegistry()

    def test_empty_registry(self):
        assert self.registry.sections == []
        assert self.registry.dashboard_widgets == []
        assert self.registry.topbar_actions == []
        assert self.registry.global_actions == []

    def test_register_section(self):
        section = CabinetSection(label="Booking", icon="bi-calendar", order=10)
        self.registry.register("booking", section=section)
        assert len(self.registry.sections) == 1
        assert self.registry.sections[0].label == "Booking"

    def test_sections_sorted_by_order(self):
        self.registry.register("b", section=CabinetSection(label="B", icon="bi-b", order=20))
        self.registry.register("a", section=CabinetSection(label="A", icon="bi-a", order=10))
        labels = [s.label for s in self.registry.sections]
        assert labels == ["A", "B"]

    def test_sections_filtering_by_group(self):
        s_admin = CabinetSection(label="Admin", icon="icon", nav_group="admin", order=1)
        s_client = CabinetSection(label="Client", icon="icon", nav_group="client", order=2)

        self.registry.register("admin_mod", section=s_admin)
        self.registry.register("client_mod", section=s_client)

        # All sections
        assert len(self.registry.sections) == 2

        # Filter by group
        admin_sections = self.registry.get_sections("admin")
        assert len(admin_sections) == 1
        assert admin_sections[0].label == "Admin"

        client_sections = self.registry.get_sections("client")
        assert len(client_sections) == 1
        assert client_sections[0].label == "Client"

    def test_register_dashboard_widget(self):
        # Traditional string registration
        self.registry.register("booking", dashboard_widget="booking/widgets/upcoming.html")
        assert len(self.registry.dashboard_widgets) == 1
        widget = self.registry.dashboard_widgets[0]
        assert isinstance(widget, DashboardWidget)
        assert widget.template == "booking/widgets/upcoming.html"

    def test_register_structured_dashboard_widget(self):
        widget = DashboardWidget(template="test.html", nav_group="client")
        self.registry.register("test_mod", dashboard_widget=widget)
        assert len(self.registry.dashboard_widgets) == 1
        assert self.registry.dashboard_widgets[0].nav_group == "client"

    def test_widgets_filtering_by_group(self):
        w_admin = DashboardWidget(template="admin.html", nav_group="admin", order=1)
        w_client = DashboardWidget(template="client.html", nav_group="client", order=2)

        self.registry.register("admin_mod", dashboard_widget=w_admin)
        self.registry.register("client_mod", dashboard_widget=w_client)

        # Filter by group
        admin_widgets = self.registry.get_dashboard_widgets("admin")
        assert len(admin_widgets) == 1
        assert admin_widgets[0].template == "admin.html"

        client_widgets = self.registry.get_dashboard_widgets("client")
        assert len(client_widgets) == 1
        assert client_widgets[0].template == "client.html"

    def test_register_topbar_actions(self):
        actions = [NavAction(label="New", url="booking:new", icon="bi-plus")]
        self.registry.register("booking", topbar_actions=actions)
        assert len(self.registry.topbar_actions) == 1
        assert self.registry.topbar_actions[0].label == "New"

    def test_register_global_actions(self):
        actions = [NavAction(label="Export", url="booking:export")]
        self.registry.register("booking", actions=actions)
        assert len(self.registry.global_actions) == 1


@pytest.mark.unit
class TestDeclare:
    def test_declare_with_valid_section_ok(self):
        section = CabinetSection(label="Booking", icon="bi-calendar")
        from codex_django.cabinet.registry import cabinet_registry

        before = len(cabinet_registry._sections)
        declare("booking_test_valid", section=section)
        assert len(cabinet_registry._sections) >= before

    def test_declare_with_dict_section_raises(self):
        with pytest.raises(ImproperlyConfigured, match="CabinetSection instance"):
            declare("booking", section={"label": "Booking"})  # type: ignore[arg-type]

    def test_declare_with_none_section_ok(self):
        declare("reporting_widget_only", section=None, dashboard_widget="reporting/kpi.html")

    def test_declare_with_structured_widget_ok(self):
        widget = DashboardWidget(template="kpi.html")
        declare("test_structured", dashboard_widget=widget)
