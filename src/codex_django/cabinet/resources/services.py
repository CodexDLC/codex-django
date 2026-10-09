"""Services for cabinet resource persistence, permissions, and smart handlers."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, cast

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import models
from django.http import HttpRequest
from django.utils.module_loading import import_string

from .contracts import CabinetResource, SmartCreateHandlerProtocol
from .forms import build_resource_form_class
from .urls import resource_url


def user_can_resource_action(user: Any, resource: CabinetResource, action: str) -> bool:
    """Return whether ``user`` can perform a resource action."""
    explicit_perm = resource.permissions.get(action)
    if explicit_perm is not None:
        return explicit_perm == "" or bool(getattr(user, "has_perm", lambda _perm: False)(explicit_perm))

    permission_action = {
        "list": "view",
        "create": "add",
        "edit": "change",
        "publish": "add",
    }.get(action, action)
    perm = f"{resource.model._meta.app_label}.{permission_action}_{resource.model._meta.model_name}"
    return bool(getattr(user, "has_perm", lambda _perm: False)(perm))


def require_resource_permission(user: Any, resource: CabinetResource, action: str) -> None:
    """Raise ``PermissionDenied`` when ``user`` cannot perform an action."""
    if not user_can_resource_action(user, resource, action):
        raise PermissionDenied


def save_resource_from_request(
    request: HttpRequest,
    resource: CabinetResource,
    *,
    instance: models.Model | None = None,
) -> tuple[bool, Any]:
    """Validate and save a normal resource form from a request."""
    form_class = build_resource_form_class(resource)
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        return True, form.save()
    return False, form


def resolve_smart_handler(resource: CabinetResource) -> SmartCreateHandlerProtocol:
    """Instantiate a project-provided smart-create handler."""
    handler_ref = resource.smart_handler
    if handler_ref is None:
        raise ImproperlyConfigured(
            f"Cabinet resource '{resource.key}' has smart_create=True but no smart_handler is configured"
        )
    if isinstance(handler_ref, str):
        handler_ref = import_string(handler_ref)
    handler = handler_ref() if isinstance(handler_ref, type) else handler_ref
    return cast(SmartCreateHandlerProtocol, handler)


def request_payload(request: HttpRequest) -> dict[str, Any]:
    """Parse JSON or form-encoded request payload."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        if not request.body:
            return {}
        payload = json.loads(request.body.decode(request.encoding or "utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("JSON payload must be an object")
        return payload
    return {key: value for key, value in request.POST.items() if key != "csrfmiddlewaretoken"}


def smart_job_ref_payload(resource: CabinetResource, draft_id: str, payload: Any) -> dict[str, Any]:
    """Convert a handler job reference into a JSON-ready dict with default URLs."""
    data = _dto_payload(payload)
    data.setdefault("draft_id", draft_id)
    data["status_url"] = data.get("status_url") or resource_url(
        "resource_smart_status", resource_key=resource.key, draft_id=draft_id
    )
    data["publish_url"] = data.get("publish_url") or resource_url(
        "resource_smart_publish", resource_key=resource.key, draft_id=draft_id
    )
    return data


def dto_payload(payload: Any) -> dict[str, Any]:
    """Convert dataclass DTOs to JSON-ready dictionaries."""
    return _dto_payload(payload)


def _dto_payload(payload: Any) -> dict[str, Any]:
    if is_dataclass(payload) and not isinstance(payload, type):
        return asdict(payload)
    if isinstance(payload, dict):
        return dict(payload)
    raise TypeError(f"Expected dataclass or dict payload, got {type(payload)}")
