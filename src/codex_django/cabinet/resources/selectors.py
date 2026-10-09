"""Selectors for generic cabinet resource pages."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from django.db import models
from django.utils import formats, timezone
from django.utils.module_loading import import_string

from codex_django.cabinet.types import DataTableData, TableAction, TableColumn

from .contracts import CabinetResource, CabinetResourceListColumn
from .services import user_can_resource_action
from .urls import resource_url


def build_resource_list_context(request: Any, resource: CabinetResource) -> dict[str, Any]:
    """Build template context for a resource list page."""
    columns = [_table_column(column, index) for index, column in enumerate(resource.normalized_list_columns)]
    rows = _resource_rows(request, resource)
    search_query = _search_query(request)
    actions = []
    if resource.edit_enabled and user_can_resource_action(request.user, resource, "edit"):
        actions.append(
            TableAction(label="Edit", url_key="edit_url", icon="bi-pencil-square", style="btn-outline-secondary")
        )

    create_url = ""
    create_label = ""
    if resource.create_enabled and user_can_resource_action(request.user, resource, "create"):
        create_url = resource_url("resource_create", resource_key=resource.key)
        create_label = resource.create_label or f"Add {resource.singular_title}"

    return {
        "resource": resource,
        "title": resource.title,
        "subtitle": resource.section,
        "btn_label": create_label,
        "btn_url": create_url,
        "btn_icon": "bi-plus-lg",
        "table": DataTableData(
            columns=columns,
            rows=rows,
            actions=actions,
            search_placeholder=_search_placeholder(resource),
            search_query=search_query,
            search_param="q",
            search_action=getattr(request, "path", ""),
            empty_message=f"No {resource.title.lower()} yet",
        ),
    }


def _table_column(column: CabinetResourceListColumn, index: int) -> TableColumn:
    return TableColumn(
        key=column.name,
        label=column.label or _prettify_name(column.name),
        sortable=column.sortable,
        bold=index == 0,
    )


def _row_for_object(resource: CabinetResource, obj: models.Model) -> dict[str, Any]:
    row = {column.name: _display_model_value(obj, column.name) for column in resource.normalized_list_columns}
    row["pk"] = obj.pk
    row["id"] = obj.pk
    if resource.edit_enabled:
        row["edit_url"] = resource_url("resource_edit", resource_key=resource.key, pk=obj.pk)
    return row


def _resource_rows(request: Any, resource: CabinetResource) -> list[dict[str, Any]]:
    if resource.list_selector is None:
        rows = [_row_for_object(resource, obj) for obj in resource.model._default_manager.all()]
        return _filter_default_rows(resource, rows, _search_query(request))

    selector = _resolve_list_selector(resource)
    rows = []
    for item in selector(request, resource):
        row = _row_from_selector_item(item)
        _ensure_standard_row_urls(resource, row)
        _format_row_values(resource, row)
        rows.append(row)
    return rows


def _filter_default_rows(resource: CabinetResource, rows: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    searchable_columns = _searchable_columns(resource)
    if not query or not searchable_columns:
        return rows
    normalized_query = query.casefold()
    return [
        row
        for row in rows
        if any(normalized_query in str(row.get(column.name, "")).casefold() for column in searchable_columns)
    ]


def _resolve_list_selector(resource: CabinetResource) -> Any:
    if isinstance(resource.list_selector, str):
        return import_string(resource.list_selector)
    return resource.list_selector


def _row_from_selector_item(item: Any) -> dict[str, Any]:
    if is_dataclass(item) and not isinstance(item, type):
        return asdict(item)
    if isinstance(item, Mapping):
        return dict(item)
    if hasattr(item, "_asdict"):
        return dict(item._asdict())
    if hasattr(item, "__dict__"):
        return dict(vars(item))
    raise TypeError(f"Cabinet resource list selector rows must be dict or DTO objects, got {type(item)}")


def _ensure_standard_row_urls(resource: CabinetResource, row: dict[str, Any]) -> None:
    if not resource.edit_enabled or row.get("edit_url"):
        return
    pk = row.get("pk", row.get("id"))
    if pk not in (None, ""):
        row["edit_url"] = resource_url("resource_edit", resource_key=resource.key, pk=pk)


def _format_row_values(resource: CabinetResource, row: dict[str, Any]) -> None:
    for column in resource.normalized_list_columns:
        if column.name in row:
            row[column.name] = _format_cell_value(row[column.name])


def _display_model_value(obj: models.Model, name: str) -> str:
    value = getattr(obj, name, "")
    if callable(value):
        value = value()
    return _format_cell_value(value)


def _format_cell_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return formats.date_format(value, "SHORT_DATETIME_FORMAT")
    if isinstance(value, date):
        return formats.date_format(value, "SHORT_DATE_FORMAT")
    if isinstance(value, Decimal):
        return formats.number_format(value, decimal_pos=2, force_grouping=True)
    return str(value)


def _search_placeholder(resource: CabinetResource) -> str:
    if resource.search_enabled and _searchable_columns(resource):
        return f"Search {resource.title.lower()}..."
    return ""


def _search_query(request: Any) -> str:
    return str(getattr(request, "GET", {}).get("q", "")).strip()


def _searchable_columns(resource: CabinetResource) -> tuple[CabinetResourceListColumn, ...]:
    return tuple(column for column in resource.normalized_list_columns if column.searchable)


def _prettify_name(name: str) -> str:
    return name.replace("_", " ").strip().title()
