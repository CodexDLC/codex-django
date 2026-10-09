"""Registry and validation for generic cabinet resources."""

from __future__ import annotations

from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db import models

from .contracts import CabinetResource, CabinetResourceField, CabinetResourceListColumn


class CabinetResourceRegistry:
    """Store model resource declarations in process memory."""

    def __init__(self) -> None:
        self._resources: dict[str, CabinetResource] = {}

    def register(self, resource: CabinetResource) -> CabinetResource:
        """Validate and register a cabinet resource."""
        self._validate_resource(resource)
        if resource.key in self._resources:
            raise ImproperlyConfigured(f"Cabinet resource key must be unique: '{resource.key}' is already registered")
        self._resources[resource.key] = resource
        return resource

    def get(self, key: str) -> CabinetResource:
        """Return a registered resource by key."""
        try:
            return self._resources[key]
        except KeyError as exc:
            raise KeyError(f"Cabinet resource '{key}' is not registered") from exc

    def all(self) -> list[CabinetResource]:
        """Return all resources in registration order."""
        return list(self._resources.values())

    def by_section(self, section: str) -> list[CabinetResource]:
        """Return resources registered under a section."""
        return [resource for resource in self._resources.values() if resource.section == section]

    def registered_keys(self) -> list[str]:
        """Return registered resource keys."""
        return list(self._resources)

    def _validate_resource(self, resource: CabinetResource) -> None:
        if not isinstance(resource, CabinetResource):
            raise ImproperlyConfigured(f"register() expects CabinetResource, got {type(resource)}")
        if not resource.key or not resource.key.strip():
            raise ImproperlyConfigured("CabinetResource.key must be non-empty")
        if not isinstance(resource.model, type) or not issubclass(resource.model, models.Model):
            raise ImproperlyConfigured("CabinetResource.model must be a Django Model class")
        has_valid_selector = callable(resource.list_selector) or (
            isinstance(resource.list_selector, str) and bool(resource.list_selector.strip())
        )
        if resource.list_selector is not None and not has_valid_selector:
            raise ImproperlyConfigured("CabinetResource.list_selector must be a callable or non-empty import path")
        if resource.smart_create and not resource.form_fields:
            raise ImproperlyConfigured("CabinetResource.smart_create requires form_fields")

        for field in resource.normalized_form_fields:
            self._validate_form_field(resource, field)
        for column in resource.normalized_list_columns:
            self._validate_list_column(resource, column)

    def _validate_form_field(self, resource: CabinetResource, field: CabinetResourceField) -> None:
        if not field.name:
            raise ImproperlyConfigured(f"CabinetResource '{resource.key}' has a form field with an empty name")
        if field.virtual:
            return
        if not _model_field_exists(resource.model, field.name):
            raise ImproperlyConfigured(
                f"CabinetResource '{resource.key}' form field '{field.name}' does not exist on "
                f"{resource.model.__name__}; mark it virtual=True to allow virtual fields"
            )

    def _validate_list_column(self, resource: CabinetResource, column: CabinetResourceListColumn) -> None:
        if not column.name:
            raise ImproperlyConfigured(f"CabinetResource '{resource.key}' has a list column with an empty name")
        if column.virtual or resource.list_selector is not None:
            return
        if _model_field_exists(resource.model, column.name) or hasattr(resource.model, column.name):
            return
        raise ImproperlyConfigured(
            f"CabinetResource '{resource.key}' list column '{column.name}' does not exist on "
            f"{resource.model.__name__}; mark it virtual=True to allow virtual columns"
        )


def _model_field_exists(model: type[models.Model], field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
    except FieldDoesNotExist:
        return False
    return True


cabinet_resource_registry = CabinetResourceRegistry()
