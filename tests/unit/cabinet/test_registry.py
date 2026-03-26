"""Unit tests for CabinetRegistry and declare()."""

from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured

from codex_django.cabinet.registry import CabinetRegistry, declare
from codex_django.cabinet.types import CabinetSection, NavAction


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

    def test_multiple_modules_same_order_stable(self):
        self.registry.register("x", section=CabinetSection(label="X", icon="bi-x", order=10))
        self.registry.register("y", section=CabinetSection(label="Y", icon="bi-y", order=10))
        assert len(self.registry.sections) == 2

    def test_register_dashboard_widget(self):
        self.registry.register("booking", dashboard_widget="booking/widgets/upcoming.html")
        assert "booking/widgets/upcoming.html" in self.registry.dashboard_widgets

    def test_multiple_dashboard_widgets(self):
        self.registry.register("booking", dashboard_widget="booking/widgets/upcoming.html")
        self.registry.register("catalog", dashboard_widget="catalog/widgets/stats.html")
        assert len(self.registry.dashboard_widgets) == 2

    def test_register_topbar_actions(self):
        actions = [NavAction(label="New", url="booking:new", icon="bi-plus")]
        self.registry.register("booking", topbar_actions=actions)
        assert len(self.registry.topbar_actions) == 1
        assert self.registry.topbar_actions[0].label == "New"

    def test_register_global_actions(self):
        actions = [NavAction(label="Export", url="booking:export")]
        self.registry.register("booking", actions=actions)
        assert len(self.registry.global_actions) == 1

    def test_register_without_section_no_crash(self):
        # Widget-only registration (no section in nav)
        self.registry.register("reporting", dashboard_widget="reporting/kpi.html")
        assert self.registry.sections == []
        assert len(self.registry.dashboard_widgets) == 1

    def test_overwriting_same_module_replaces_section(self):
        s1 = CabinetSection(label="Old", icon="bi-x", order=10)
        s2 = CabinetSection(label="New", icon="bi-x", order=10)
        self.registry.register("booking", section=s1)
        self.registry.register("booking", section=s2)
        assert len(self.registry.sections) == 1
        assert self.registry.sections[0].label == "New"


@pytest.mark.unit
class TestDeclare:
    def test_declare_with_valid_section_ok(self):
        section = CabinetSection(label="Booking", icon="bi-calendar")
        # Should not raise — uses global cabinet_registry but that's fine for this check
        from codex_django.cabinet.registry import cabinet_registry
        before = len(cabinet_registry._sections)
        declare("booking_test_valid", section=section)
        assert len(cabinet_registry._sections) >= before

    def test_declare_with_dict_section_raises(self):
        with pytest.raises(ImproperlyConfigured, match="CabinetSection instance"):
            declare("booking", section={"label": "Booking"})  # type: ignore[arg-type]

    def test_declare_with_none_section_ok(self):
        # Widget-only — no section in nav
        declare("reporting_widget_only", section=None, dashboard_widget="reporting/kpi.html")

    def test_declare_wrong_type_error_message(self):
        with pytest.raises(ImproperlyConfigured) as exc_info:
            declare("test", section="not_a_section")  # type: ignore[arg-type]
        assert "CabinetSection instance" in str(exc_info.value)
