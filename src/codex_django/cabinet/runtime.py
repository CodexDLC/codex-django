"""Runtime context resolution for cabinet shells.

The resolver is intentionally project-agnostic. It converts a Django request
plus registry declarations into a stable cabinet context without hardcoding a
single project URL shape.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from typing import Any

from django.conf import settings
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse

from .registry import CabinetRegistry, cabinet_registry
from .types import Shortcut, SidebarItem, TopbarEntry


@dataclass(frozen=True)
class CabinetSpaceConfig:
    """URL and fallback policy for one cabinet space."""

    name: str
    prefixes: tuple[str, ...] = ()
    default_module: str = "admin"
    nav_group: str | None = None
    settings_url_name: str | None = "cabinet:site_settings"


@dataclass(frozen=True)
class CabinetRequestContext:
    """Resolved cabinet shell data for a request."""

    space: str
    module: str
    sidebar: list[SidebarItem] = field(default_factory=list)
    shortcuts: list[Shortcut] = field(default_factory=list)
    topbar_entries: list[TopbarEntry] = field(default_factory=list)
    branding: dict[str, Any] = field(default_factory=dict)
    active_topbar: TopbarEntry | None = None
    settings_url: str | None = None
    nav_group: str | None = None


class CabinetRuntimeResolver:
    """Resolve cabinet space/module metadata from a request and registry."""

    def __init__(
        self,
        registry: CabinetRegistry | None = None,
        *,
        default_space: str = "staff",
        default_module: str = "admin",
    ) -> None:
        self.registry = registry or cabinet_registry
        self.default_space = default_space
        self.default_module = default_module

    def get_space_configs(self) -> dict[str, CabinetSpaceConfig]:
        """Return space configuration from Django settings with safe defaults."""
        raw_spaces = getattr(settings, "CODEX_CABINET_SPACES", None) or {}
        configs: dict[str, CabinetSpaceConfig] = {
            "staff": CabinetSpaceConfig(
                name="staff",
                prefixes=_normalize_prefixes(getattr(settings, "CODEX_CABINET_STAFF_PREFIXES", ("/cabinet/",))),
                default_module=self.default_module,
                settings_url_name="cabinet:site_settings",
            ),
            "client": CabinetSpaceConfig(
                name="client",
                prefixes=_normalize_prefixes(getattr(settings, "CODEX_CABINET_CLIENT_PREFIXES", ("/cabinet/my/",))),
                default_module="client",
                nav_group="client",
                settings_url_name=None,
            ),
        }

        if isinstance(raw_spaces, dict):
            for name, value in raw_spaces.items():
                if not isinstance(value, dict):
                    continue
                base = configs.get(str(name), CabinetSpaceConfig(name=str(name)))
                configs[str(name)] = CabinetSpaceConfig(
                    name=str(name),
                    prefixes=_normalize_prefixes(value.get("prefixes", base.prefixes)),
                    default_module=str(value.get("default_module", base.default_module)),
                    nav_group=value.get("nav_group", base.nav_group),
                    settings_url_name=value.get("settings_url_name", base.settings_url_name),
                )

        return configs

    def detect_space(self, request: HttpRequest) -> str:
        explicit: str | None = getattr(request, "cabinet_space", None)
        if explicit:
            return str(explicit)

        path = getattr(request, "path", "") or ""
        configs = self.get_space_configs()
        candidates: list[tuple[int, str]] = []
        for name, config in configs.items():
            for prefix in config.prefixes:
                if prefix and path.startswith(prefix):
                    candidates.append((len(prefix), name))

        if candidates:
            return sorted(candidates, reverse=True)[0][1]
        return self.default_space

    def detect_module(self, request: HttpRequest, space: str) -> str:
        explicit: str | None = getattr(request, "cabinet_module", None)
        if explicit:
            return str(explicit)

        match = getattr(request, "resolver_match", None)
        app_name = getattr(match, "app_name", None)
        if app_name and app_name != "cabinet":
            return str(app_name)

        config = self.get_space_configs().get(space)
        return (
            self.registry.get_default_module(space)
            or (config.default_module if config else None)
            or self.default_module
        )

    def resolve_settings_url(self, space: str, module: str) -> str | None:
        custom_url = self.registry.get_settings_url(space, module)
        if custom_url:
            return _reverse_or_literal(custom_url)

        config = self.get_space_configs().get(space)
        if not config or not config.settings_url_name:
            return None
        return _reverse_or_none(config.settings_url_name)

    def get_context(self, request: HttpRequest) -> CabinetRequestContext:
        space = self.detect_space(request)
        module = self.detect_module(request, space)
        nav_group = getattr(request, "cabinet_nav_group", None)
        if nav_group is None:
            config = self.get_space_configs().get(space)
            nav_group = config.nav_group if config else None

        return CabinetRequestContext(
            space=space,
            module=module,
            sidebar=self.registry.get_sidebar(space, module),
            shortcuts=self.registry.get_shortcuts(space, module),
            topbar_entries=self.registry.get_topbar_entries(),
            branding=self.registry.get_branding(space),
            active_topbar=self.registry.get_module_topbar(module),
            settings_url=self.resolve_settings_url(space, module),
            nav_group=nav_group,
        )


def _normalize_prefixes(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list | tuple | set):
        return tuple(str(item) for item in value if str(item))
    return ()


def _reverse_or_literal(value: str) -> str:
    try:
        return reverse(value)
    except NoReverseMatch:
        return value


def _reverse_or_none(value: str) -> str | None:
    with contextlib.suppress(NoReverseMatch):
        return reverse(value)
    return None
