"""Unit tests for cabinet types (dataclasses)."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from codex_django.cabinet.types import CabinetSection, ListItem, NavAction, TableColumn


@pytest.mark.unit
class TestCabinetSection:
    def test_valid_admin_group(self):
        s = CabinetSection(label="Dashboard", icon="bi-house", nav_group="admin")
        assert s.nav_group == "admin"

    def test_valid_services_group(self):
        s = CabinetSection(label="Booking", icon="bi-calendar", nav_group="services")
        assert s.nav_group == "services"

    def test_invalid_nav_group_raises(self):
        from django.core.exceptions import ImproperlyConfigured

        with pytest.raises(ImproperlyConfigured, match="nav_group"):
            CabinetSection(label="X", icon="bi-x", nav_group="invalid")

    def test_frozen_immutable(self):
        s = CabinetSection(label="X", icon="bi-x")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            s.label = "Y"  # type: ignore[misc]

    def test_default_values(self):
        s = CabinetSection(label="X", icon="bi-x")
        assert s.nav_group == "admin"
        assert s.url is None
        assert s.permissions == ()
        assert s.order == 99

    def test_permissions_is_tuple(self):
        s = CabinetSection(label="X", icon="bi-x", permissions=("app.view_model",))
        assert isinstance(s.permissions, tuple)
        assert "app.view_model" in s.permissions

    def test_url_can_be_set(self):
        s = CabinetSection(label="X", icon="bi-x", url="booking:index")
        assert s.url == "booking:index"

    def test_order_custom(self):
        s = CabinetSection(label="X", icon="bi-x", order=5)
        assert s.order == 5


@pytest.mark.unit
class TestNavAction:
    def test_creation_with_icon(self):
        a = NavAction(label="New", url="booking:new", icon="bi-plus")
        assert a.label == "New"
        assert a.url == "booking:new"
        assert a.icon == "bi-plus"

    def test_icon_is_optional(self):
        a = NavAction(label="Export", url="booking:export")
        assert a.icon is None


@pytest.mark.unit
class TestTableColumn:
    def test_defaults(self):
        col = TableColumn(key="name", label="Name")
        assert col.align == "left"
        assert col.bold is False
        assert col.muted is False
        assert col.sortable is False
        assert col.badge_key is None
        assert col.icon_key is None

    def test_custom_values(self):
        col = TableColumn(key="revenue", label="Revenue", align="right", bold=True)
        assert col.align == "right"
        assert col.bold is True


@pytest.mark.unit
class TestListItem:
    def test_required_fields(self):
        item = ListItem(label="John Doe", value="5 visits")
        assert item.label == "John Doe"
        assert item.value == "5 visits"
        assert item.avatar is None
        assert item.sublabel is None
        assert item.subvalue is None

    def test_all_fields(self):
        item = ListItem(label="A", value="B", avatar="JD", sublabel="sub", subvalue="sv")
        assert item.avatar == "JD"
        assert item.sublabel == "sub"
        assert item.subvalue == "sv"
