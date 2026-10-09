"""Thin views for generic cabinet resources."""

from __future__ import annotations

from typing import cast

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from codex_django.cabinet.resources import cabinet_resource_registry
from codex_django.cabinet.resources.forms import build_resource_form_class
from codex_django.cabinet.resources.selectors import build_resource_list_context
from codex_django.cabinet.resources.services import (
    dto_payload,
    request_payload,
    require_resource_permission,
    resolve_smart_handler,
    save_resource_from_request,
    smart_job_ref_payload,
)
from codex_django.cabinet.resources.urls import resource_url


@login_required
@require_GET
def resource_list_view(request: HttpRequest, resource_key: str) -> HttpResponse:
    """Render a generic list/table page for a cabinet resource."""
    resource = cabinet_resource_registry.get(resource_key)
    _attach_cabinet_metadata(request, resource.section)
    require_resource_permission(request.user, resource, "list")
    return render(request, "cabinet/resources/list.html", build_resource_list_context(request, resource))


@login_required
def resource_create_view(request: HttpRequest, resource_key: str) -> HttpResponse:
    """Render and process normal create or smart-create shell for a resource."""
    resource = cabinet_resource_registry.get(resource_key)
    _attach_cabinet_metadata(request, resource.section)
    require_resource_permission(request.user, resource, "create")

    if resource.smart_create and resource.smart_handler:
        form_class = build_resource_form_class(resource)
        return render(
            request,
            "cabinet/resources/smart_create.html",
            {
                "resource": resource,
                "title": resource.create_label or f"Create {resource.singular_title}",
                "form": form_class(),
                "preview_url": resource_url("resource_smart_preview", resource_key=resource.key),
                "list_url": resource_url("resource_list", resource_key=resource.key),
            },
        )

    saved, result = save_resource_from_request(request, resource)
    if saved:
        return redirect(resource_url("resource_list", resource_key=resource.key))
    return render(
        request,
        "cabinet/resources/form.html",
        {
            "resource": resource,
            "title": resource.create_label or f"Create {resource.singular_title}",
            "form": result,
            "list_url": resource_url("resource_list", resource_key=resource.key),
        },
    )


@login_required
def resource_edit_view(request: HttpRequest, resource_key: str, pk: str) -> HttpResponse:
    """Render and process a normal edit form for a resource instance."""
    resource = cabinet_resource_registry.get(resource_key)
    _attach_cabinet_metadata(request, resource.section)
    require_resource_permission(request.user, resource, "edit")
    obj = get_object_or_404(resource.model, pk=pk)
    saved, result = save_resource_from_request(request, resource, instance=obj)
    if saved:
        return redirect(resource_url("resource_list", resource_key=resource.key))
    return render(
        request,
        "cabinet/resources/form.html",
        {
            "resource": resource,
            "title": f"Edit {resource.singular_title}",
            "form": result,
            "object": obj,
            "list_url": resource_url("resource_list", resource_key=resource.key),
        },
    )


@login_required
@require_POST
def resource_smart_preview_view(request: HttpRequest, resource_key: str) -> JsonResponse:
    """Submit source fields to the project smart-create handler."""
    resource = cabinet_resource_registry.get(resource_key)
    require_resource_permission(request.user, resource, "create")
    try:
        handler = resolve_smart_handler(resource)
    except ImproperlyConfigured as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    try:
        payload = request_payload(request)
    except ValueError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    form_class = build_resource_form_class(resource)
    form = form_class(payload)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors.get_json_data()}, status=400)

    job_ref = handler.create_preview_job(
        resource=resource,
        user=request.user,
        source_payload=form.cleaned_data,
        base_language=resource.base_language,
        target_languages=resource.target_languages,
    )
    return JsonResponse({"ok": True, **smart_job_ref_payload(resource, job_ref.draft_id, job_ref)})


@login_required
@require_GET
def resource_smart_status_view(request: HttpRequest, resource_key: str, draft_id: str) -> JsonResponse:
    """Return the current preview status for a smart-create draft."""
    resource = cabinet_resource_registry.get(resource_key)
    require_resource_permission(request.user, resource, "create")
    try:
        handler = resolve_smart_handler(resource)
    except ImproperlyConfigured as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    status = handler.get_preview_status(resource=resource, draft_id=draft_id, user=request.user)
    return JsonResponse({"ok": True, **dto_payload(status)})


@login_required
@require_POST
def resource_smart_publish_view(request: HttpRequest, resource_key: str, draft_id: str) -> JsonResponse:
    """Publish an edited smart-create draft via the project handler."""
    resource = cabinet_resource_registry.get(resource_key)
    require_resource_permission(request.user, resource, "publish")
    try:
        handler = resolve_smart_handler(resource)
        payload = request_payload(request)
    except (ImproperlyConfigured, ValueError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    obj = handler.publish(resource=resource, draft_id=draft_id, user=request.user, edited_payload=payload)
    return JsonResponse(
        {
            "ok": True,
            "pk": obj.pk,
            "list_url": resource_url("resource_list", resource_key=resource.key),
            "edit_url": resource_url("resource_edit", resource_key=resource.key, pk=obj.pk),
        }
    )


class _CabinetResourceRequest(HttpRequest):
    cabinet_space: str
    cabinet_module: str


def _attach_cabinet_metadata(request: HttpRequest, section: str) -> None:
    cabinet_request = cast(_CabinetResourceRequest, request)
    cabinet_request.cabinet_space = "staff"
    cabinet_request.cabinet_module = section.lower().replace(" ", "_") or "resources"
