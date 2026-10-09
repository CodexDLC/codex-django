"""Dynamic Django form builder for generic cabinet resources."""

from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Any

from django import forms
from django.db import models

from .contracts import CabinetResource, CabinetResourceField

if TYPE_CHECKING:
    _TypedModelForm = forms.ModelForm[models.Model]
else:
    _TypedModelForm = forms.ModelForm


def build_resource_form_class(resource: CabinetResource) -> type[forms.ModelForm[models.Model]]:
    """Build a ``ModelForm`` subclass from ``resource.form_fields``."""
    model_field_names = [field.name for field in resource.normalized_form_fields if not field.virtual]
    field_specs = resource.normalized_form_fields

    class CabinetDynamicResourceForm(_TypedModelForm):
        """Runtime form bound to a cabinet resource declaration."""

        class Meta:
            model = resource.model
            fields = model_field_names

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            ordered_fields: OrderedDict[str, forms.Field] = OrderedDict()
            for spec in field_specs:
                if spec.virtual:
                    field = _build_virtual_form_field(spec)
                    self.fields[spec.name] = field
                else:
                    field = self.fields[spec.name]
                    _apply_resource_field_options(field, spec, resource.model)
                ordered_fields[spec.name] = self.fields[spec.name]
            self.fields = ordered_fields

    CabinetDynamicResourceForm.__name__ = f"{resource.model.__name__}CabinetResourceForm"
    return CabinetDynamicResourceForm


def _build_virtual_form_field(spec: CabinetResourceField) -> forms.Field:
    widget = _widget_for_spec(spec, None)
    field = forms.CharField(
        label=spec.label or _prettify_name(spec.name),
        required=bool(spec.required),
        help_text=spec.help_text,
        disabled=spec.readonly,
        widget=widget,
    )
    if spec.tooltip:
        field.widget.attrs["data-cab-field-tooltip"] = spec.tooltip
    _apply_common_widget_attrs(field)
    return field


def _apply_resource_field_options(
    field: forms.Field,
    spec: CabinetResourceField,
    model: type[models.Model],
) -> None:
    model_field = model._meta.get_field(spec.name)
    field.label = spec.label or str(getattr(model_field, "verbose_name", "")) or _prettify_name(spec.name)
    if spec.required is not None:
        field.required = spec.required
    if spec.help_text:
        field.help_text = spec.help_text
    if spec.readonly:
        field.disabled = True
    widget_model_field = model_field if isinstance(model_field, models.Field) else None
    field.widget = _widget_for_spec(spec, widget_model_field) or field.widget
    if spec.tooltip:
        field.widget.attrs["data-cab-field-tooltip"] = spec.tooltip
    _apply_common_widget_attrs(field)


def _widget_for_spec(spec: CabinetResourceField, model_field: models.Field[Any, Any] | None) -> forms.Widget | None:
    widget = spec.widget.lower()
    field_format = spec.format.lower()

    if widget in {"textarea", "richtext"} or field_format in {"html", "markdown", "json"}:
        return forms.Textarea(attrs={"rows": 5})
    if widget in {"checkbox", "toggle"}:
        return forms.CheckboxInput()
    if widget == "number":
        return forms.NumberInput()
    if widget == "date":
        return forms.DateInput(attrs={"type": "date"})
    if widget in {"datetime", "datetime-local"}:
        return forms.DateTimeInput(attrs={"type": "datetime-local"})
    if widget == "text":
        return forms.TextInput()

    if isinstance(model_field, models.TextField):
        return forms.Textarea(attrs={"rows": 5})
    if isinstance(model_field, models.DateTimeField):
        return forms.DateTimeInput(attrs={"type": "datetime-local"})
    if isinstance(model_field, models.DateField):
        return forms.DateInput(attrs={"type": "date"})
    if isinstance(model_field, models.BooleanField):
        return forms.CheckboxInput()
    return None


def _apply_common_widget_attrs(field: forms.Field) -> None:
    if isinstance(field.widget, forms.CheckboxInput):
        field.widget.attrs.setdefault("class", "form-check-input")
    elif not isinstance(field.widget, forms.SelectMultiple):
        field.widget.attrs.setdefault("class", "form-control")


def _prettify_name(name: str) -> str:
    return name.replace("_", " ").strip().capitalize()
