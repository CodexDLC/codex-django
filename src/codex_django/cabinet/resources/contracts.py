"""Contracts for generic cabinet model resources and smart-create flows."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, cast

from django.db import models


@dataclass(frozen=True)
class CabinetResourceField:
    """A logical field exposed by a cabinet resource form."""

    name: str
    label: str = ""
    role: str = ""
    format: str = "plain"
    widget: str = ""
    required: bool | None = None
    help_text: str = ""
    tooltip: str = ""
    readonly: bool = False
    virtual: bool = False
    ai_enabled: bool = True


@dataclass(frozen=True)
class CabinetResourceListColumn:
    """A logical column exposed by a cabinet resource list page."""

    name: str
    label: str = ""
    sortable: bool = False
    searchable: bool = False
    virtual: bool = False


@dataclass(frozen=True)
class CabinetResource:
    """Registration payload for a Django model-backed cabinet resource."""

    key: str
    model: type[models.Model]
    section: str
    title: str
    singular_title: str = ""
    list_columns: Sequence[CabinetResourceListColumn | str] = ()
    list_selector: str | Callable[..., Any] | None = None
    search_enabled: bool = True
    form_fields: Sequence[CabinetResourceField | str] = ()
    create_enabled: bool = True
    create_label: str = ""
    edit_enabled: bool = True
    smart_create: bool = False
    smart_handler: str | type | None = None
    base_language: str = ""
    target_languages: Sequence[str] = ()
    permissions: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "list_columns",
            tuple(
                column if isinstance(column, CabinetResourceListColumn) else CabinetResourceListColumn(str(column))
                for column in self.list_columns
            ),
        )
        object.__setattr__(
            self,
            "form_fields",
            tuple(
                field if isinstance(field, CabinetResourceField) else CabinetResourceField(str(field))
                for field in self.form_fields
            ),
        )
        if not self.singular_title:
            object.__setattr__(self, "singular_title", str(self.model._meta.verbose_name).title())

    @property
    def normalized_list_columns(self) -> tuple[CabinetResourceListColumn, ...]:
        """Columns normalized from both accepted constructor input forms."""
        return cast(tuple[CabinetResourceListColumn, ...], self.list_columns)

    @property
    def normalized_form_fields(self) -> tuple[CabinetResourceField, ...]:
        """Fields normalized from both accepted constructor input forms."""
        return cast(tuple[CabinetResourceField, ...], self.form_fields)


@dataclass(frozen=True)
class SmartCreateJobRef:
    """Reference returned after scheduling a smart-create preview job."""

    draft_id: str
    status_url: str = ""
    publish_url: str = ""


@dataclass(frozen=True)
class SmartCreateLanguageState:
    """Per-language preview state returned by a smart-create handler."""

    language: str
    status: str
    fields: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    progress: int = 0
    user_editable: bool = True


@dataclass(frozen=True)
class SmartCreateStatus:
    """Preview status returned by a smart-create handler."""

    draft_id: str
    status: str
    languages: Sequence[SmartCreateLanguageState]
    error: str = ""


class SmartCreateHandlerProtocol(Protocol):
    """Project-owned integration point for AI/ARQ-backed create previews."""

    def create_preview_job(
        self,
        *,
        resource: CabinetResource,
        user: Any,
        source_payload: dict[str, Any],
        base_language: str,
        target_languages: Sequence[str],
    ) -> SmartCreateJobRef: ...

    def get_preview_status(
        self,
        *,
        resource: CabinetResource,
        draft_id: str,
        user: Any,
    ) -> SmartCreateStatus: ...

    def publish(
        self,
        *,
        resource: CabinetResource,
        draft_id: str,
        user: Any,
        edited_payload: dict[str, Any],
    ) -> models.Model: ...
