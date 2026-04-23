"""Unit tests for cabinet context processor."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from django.template.loader import render_to_string
from django.test import RequestFactory, override_settings

from codex_django.cabinet.context_processors import cabinet
from codex_django.cabinet.registry import CabinetRegistry, configure_space
from codex_django.cabinet.types import CabinetSection, SidebarItem, TopbarEntry


def _make_anon_request():
    factory = RequestFactory()
    request = factory.get("/cabinet/")
    request.user = MagicMock(is_authenticated=False)
    return request


def _make_auth_request(perms: tuple = (), path: str = "/cabinet/"):
    factory = RequestFactory()
    request = factory.get(path)
    user = MagicMock(is_authenticated=True)
    user.is_staff = False
    user.is_superuser = False
    user.has_perm = lambda p: p in perms
    request.user = user
    return request


def _make_user(is_staff: bool = False, is_superuser: bool = False):
    user = MagicMock(is_authenticated=True)
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.has_perm.return_value = True
    user.username = "tester"
    user.first_name = ""
    user.last_name = ""
    user.get_full_name.return_value = ""
    return user


@pytest.mark.unit
class TestCabinetContextProcessorAnonymous:
    def test_anonymous_returns_empty_nav(self):
        from codex_django.cabinet.context_processors import cabinet

        result = cabinet(_make_anon_request())

        assert result["cabinet_nav"] == []
        assert result["cabinet_topbar_actions"] == []
        assert result["cabinet_dashboard_widgets"] == []
        assert result["cabinet_settings"] is None
        assert result["cabinet_site_url"] == "/"
        assert result["cabinet_client_switch_url"] == "/cabinet/my/"
        assert result["cabinet_staff_switch_url"] == "/cabinet/"
        assert result["cabinet_logout_url"] == "/accounts/logout/"

    def test_anonymous_never_calls_redis(self):
        from codex_django.cabinet.context_processors import cabinet

        with patch("codex_django.cabinet.services.site_settings.SiteSettingsService.get_all_settings") as mock_get:
            cabinet(_make_anon_request())
            mock_get.assert_not_called()


@pytest.mark.unit
class TestCabinetContextProcessorAuthenticated:
    def _call(self, registry: CabinetRegistry, perms: tuple = (), path: str = "/cabinet/"):
        from codex_django.cabinet.context_processors import cabinet

        with (
            patch("codex_django.cabinet.context_processors.cabinet_registry", registry),
            patch("codex_django.cabinet.services.site_settings.SiteSettingsService.get_all_settings") as mock_get,
        ):
            mock_get.return_value = {"cabinet_name": "Test"}
            return cabinet(_make_auth_request(perms=perms, path=path))

    def test_authenticated_gets_open_sections(self):
        registry = CabinetRegistry()
        registry.register("booking", section=CabinetSection(label="Booking", icon="bi-calendar"))

        result = self._call(registry)

        assert len(result["cabinet_nav"]) == 1
        assert result["cabinet_nav"][0].label == "Booking"

    def test_cabinet_settings_loaded_from_redis(self):
        registry = CabinetRegistry()
        result = self._call(registry)
        assert result["cabinet_settings"] == {"cabinet_name": "Test"}

    def test_section_with_no_permissions_always_visible(self):
        registry = CabinetRegistry()
        registry.register("open", section=CabinetSection(label="Open", icon="bi-x", permissions=()))

        result = self._call(registry, perms=())
        assert len(result["cabinet_nav"]) == 1

    def test_section_hidden_when_user_lacks_permission(self):
        registry = CabinetRegistry()
        registry.register(
            "admin", section=CabinetSection(label="Admin", icon="bi-gear", permissions=("system.change_settings",))
        )

        result = self._call(registry, perms=())
        assert result["cabinet_nav"] == []

    def test_section_visible_when_user_has_permission(self):
        registry = CabinetRegistry()
        registry.register(
            "admin", section=CabinetSection(label="Admin", icon="bi-gear", permissions=("system.change_settings",))
        )

        result = self._call(registry, perms=("system.change_settings",))
        assert len(result["cabinet_nav"]) == 1

    def test_or_logic_one_of_two_permissions(self):
        """Section visible if user has AT LEAST ONE matching permission."""
        registry = CabinetRegistry()
        registry.register(
            "section", section=CabinetSection(label="X", icon="bi-x", permissions=("app.view_a", "app.view_b"))
        )

        result = self._call(registry, perms=("app.view_b",))
        assert len(result["cabinet_nav"]) == 1

    def test_nav_order_preserved(self):
        registry = CabinetRegistry()
        registry.register("z", section=CabinetSection(label="Z", icon="bi-z", order=30))
        registry.register("a", section=CabinetSection(label="A", icon="bi-a", order=10))
        registry.register("m", section=CabinetSection(label="M", icon="bi-m", order=20))

        result = self._call(registry)
        labels = [s.label for s in result["cabinet_nav"]]
        assert labels == ["A", "M", "Z"]

    def test_runtime_resolver_uses_registered_default_module(self):
        registry = CabinetRegistry()
        registry.register_v2(
            "booking",
            space="staff",
            topbar=TopbarEntry(group="services", label="Booking", icon="bi-calendar", url="/cabinet/booking/"),
            sidebar=[SidebarItem(label="Schedule", url="booking:schedule")],
        )

        result = self._call(registry)

        assert result["cabinet_active_module"] == "booking"
        assert result["cabinet_sidebar"][0].label == "Schedule"

    @override_settings(
        CODEX_CABINET_SPACES={"client": {"prefixes": ("/account/",), "default_module": "portal", "nav_group": "client"}}
    )
    def test_runtime_resolver_accepts_custom_client_prefix(self):
        registry = CabinetRegistry()
        result = self._call(registry, path="/account/")

        assert result["cabinet_space"] == "client"
        assert result["cabinet_active_module"] == "portal"

    @override_settings(
        CODEX_CABINET_SITE_URL="/home/",
        CODEX_CABINET_CLIENT_URL_NAME="/profile/",
        CODEX_CABINET_STAFF_URL_NAME="/staff/",
        CODEX_CABINET_LOGOUT_URL_NAME="/logout/",
    )
    def test_shell_urls_are_available_for_topbar_navigation(self):
        registry = CabinetRegistry()
        result = self._call(registry)

        assert result["cabinet_site_url"] == "/home/"
        assert result["cabinet_client_switch_url"] == "/profile/"
        assert result["cabinet_staff_switch_url"] == "/staff/"
        assert result["cabinet_logout_url"] == "/logout/"

    def test_staff_topbar_uses_safe_shell_urls_without_account_routes(self):
        request = _make_auth_request()
        request.user.get_full_name.return_value = "Admin User"
        html = render_to_string(
            "cabinet/includes/_topbar.html",
            {
                "request": request,
                "cabinet_nav": [],
                "cabinet_topbar_entries": [],
                "cabinet_quick_access": [],
                "cabinet_topbar_actions": [],
                "notification_items": [],
                "cabinet_site_url": "/",
                "cabinet_client_switch_url": "/cabinet/my/",
                "cabinet_logout_url": "/accounts/logout/",
            },
        )

        assert 'href="/"' in html
        assert 'href="/cabinet/my/"' in html
        assert 'href="/accounts/logout/"' in html

    def test_configure_space_client_branding_reaches_client_context(self):
        registry = CabinetRegistry()
        request = _make_auth_request(path="/cabinet/my/")

        with (
            patch("codex_django.cabinet.registry.cabinet_registry", registry),
            patch("codex_django.cabinet.context_processors.cabinet_registry", registry),
            patch("codex_django.cabinet.services.site_settings.SiteSettingsService.get_all_settings") as mock_get,
        ):
            configure_space(space="client", label="LILY", icon="bi-flower1")
            mock_get.return_value = {}
            result = cabinet(request)

        assert result["cabinet_space"] == "client"
        assert result["cabinet_branding"] == {"label": "LILY", "icon": "bi-flower1"}

    def test_client_sidebar_renders_branding_and_badge_key(self):
        html = render_to_string(
            "cabinet/includes/_sidebar_client.html",
            {
                "SITE_NAME": "Fallback",
                "cabinet_branding": {"label": "LILY", "icon": "bi-flower1"},
                "cabinet_sidebar": [
                    SidebarItem(
                        label="Messages",
                        url="/cabinet/my/messages/",
                        icon="bi-chat",
                        badge_key="unread_messages_count",
                    )
                ],
                "unread_messages_count": 7,
            },
        )

        assert "bi-flower1" in html
        assert "LILY" in html
        assert ">App<" not in html
        assert '<span class="cab-nav__badge">7</span>' in html

    def test_non_staff_client_context_hides_staff_switch_url(self):
        registry = CabinetRegistry()
        request = _make_auth_request(path="/cabinet/my/")
        request.user = _make_user(is_staff=False, is_superuser=False)

        with (
            patch("codex_django.cabinet.context_processors.cabinet_registry", registry),
            patch("codex_django.cabinet.services.site_settings.SiteSettingsService.get_all_settings") as mock_get,
        ):
            mock_get.return_value = {}
            result = cabinet(request)

        html = render_to_string(
            "cabinet/includes/_topbar_client.html",
            {
                "request": request,
                "notification_items": [],
                "cabinet_client_dropdown_items": [],
                "cabinet_logout_url": "/accounts/logout/",
                "cabinet_staff_switch_url": result["cabinet_staff_switch_url"],
            },
        )

        assert result["cabinet_staff_switch_url"] is None
        assert "Staff area" not in html

    def test_staff_client_context_keeps_staff_switch_url(self):
        registry = CabinetRegistry()
        request = _make_auth_request(path="/cabinet/my/")
        request.user = _make_user(is_staff=True)

        with (
            patch("codex_django.cabinet.context_processors.cabinet_registry", registry),
            patch("codex_django.cabinet.services.site_settings.SiteSettingsService.get_all_settings") as mock_get,
        ):
            mock_get.return_value = {}
            result = cabinet(request)

        html = render_to_string(
            "cabinet/includes/_topbar_client.html",
            {
                "request": request,
                "notification_items": [],
                "cabinet_client_dropdown_items": [],
                "cabinet_logout_url": "/accounts/logout/",
                "cabinet_staff_switch_url": result["cabinet_staff_switch_url"],
            },
        )

        assert result["cabinet_staff_switch_url"] == "/cabinet/"
        assert 'href="/cabinet/"' in html
        assert "Staff area" in html

    @override_settings(STATIC_URL="/static/")
    def test_client_base_contains_mobile_sidebar_state_and_branding_title(self):
        request = _make_auth_request(path="/cabinet/my/")
        request.user = _make_user()

        html = render_to_string(
            "cabinet/base_client.html",
            {
                "request": request,
                "cabinet_branding": {"label": "LILY", "icon": "bi-flower1"},
                "cabinet_sidebar": [],
                "cabinet_tabs": [],
                "notification_items": [],
                "cabinet_client_dropdown_items": [],
                "cabinet_staff_switch_url": None,
                "cabinet_logout_url": "/accounts/logout/",
            },
        )

        assert "sidebarMobileOpen: false" in html
        assert "'cab-sidebar--open': sidebarMobileOpen" in html
        assert "cab-backdrop" in html
        assert '@click="sidebarMobileOpen = true"' in html
        assert "— LILY</title>" in html
