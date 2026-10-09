"""Public API for generic cabinet resources."""

from .contracts import (
    CabinetResource,
    CabinetResourceField,
    CabinetResourceListColumn,
    SmartCreateHandlerProtocol,
    SmartCreateJobRef,
    SmartCreateLanguageState,
    SmartCreateStatus,
)
from .forms import build_resource_form_class
from .registry import CabinetResourceRegistry, cabinet_resource_registry

__all__ = [
    "CabinetResource",
    "CabinetResourceField",
    "CabinetResourceListColumn",
    "CabinetResourceRegistry",
    "SmartCreateHandlerProtocol",
    "SmartCreateJobRef",
    "SmartCreateLanguageState",
    "SmartCreateStatus",
    "build_resource_form_class",
    "cabinet_resource_registry",
]
