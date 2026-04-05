"""Helpers for configurable cabinet quick-access links."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from .registry import cabinet_registry


def _stringify_url(value: object) -> str:
    return str(value or "")


def build_candidate_key(module: str, order: int, position: int) -> str:
    return f"{module}::{order}::{position}"


def parse_selected_keys(raw_value: object) -> set[str]:
    if isinstance(raw_value, list | tuple | set):
        return {str(item) for item in raw_value if str(item)}
    if not raw_value:
        return set()
    try:
        parsed = json.loads(str(raw_value))
    except (TypeError, ValueError):
        return set()
    if not isinstance(parsed, list):
        return set()
    return {str(item) for item in parsed if str(item)}


def get_staff_quick_access_candidates() -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}

    for (space, module), items in cabinet_registry._sidebar.items():  # noqa: SLF001
        if space != "staff" or not items:
            continue

        topbar = cabinet_registry.get_module_topbar(module)
        module_entry = grouped.setdefault(
            module,
            {
                "module": module,
                "module_label": str(topbar.label) if topbar else module.replace("_", " ").title(),
                "module_icon": topbar.icon if topbar else "bi-grid",
                "module_order": topbar.order if topbar else 999,
                "items": [],
            },
        )

        for position, item in enumerate(sorted(items, key=lambda entry: entry.order), start=1):
            module_entry["items"].append(
                {
                    "key": build_candidate_key(module, item.order, position),
                    "module": module,
                    "label": str(item.label),
                    "icon": item.icon,
                    "url": _stringify_url(item.url),
                    "order": item.order,
                    "permissions": item.permissions,
                }
            )

    return sorted(grouped.values(), key=lambda entry: (entry["module_order"], entry["module_label"]))


def get_enabled_staff_quick_access(selected_keys: Iterable[str], user: Any) -> list[dict[str, str | int]]:
    selected = {str(key) for key in selected_keys}
    enabled: list[dict[str, str | int]] = []

    for group in get_staff_quick_access_candidates():
        for item in group["items"]:
            if item["key"] not in selected:
                continue
            permissions = item["permissions"]
            if permissions and not any(user.has_perm(permission) for permission in permissions):
                continue
            enabled.append(
                {
                    "key": str(item["key"]),
                    "label": str(item["label"]),
                    "icon": str(item["icon"]),
                    "url": str(item["url"]),
                    "module": str(item["module"]),
                    "module_label": str(group["module_label"]),
                    "module_icon": str(group["module_icon"]),
                    "order": int(item["order"]),
                    "module_order": int(group["module_order"]),
                }
            )

    return sorted(enabled, key=lambda item: (int(item["module_order"]), int(item["order"]), str(item["label"])))
