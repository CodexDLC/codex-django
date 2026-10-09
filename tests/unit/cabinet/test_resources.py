from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytest
from django.db import connection, models
from django.test import override_settings
from django.urls import include, path, reverse
from django.utils import formats, timezone

from codex_django.cabinet.resources import (
    CabinetResource,
    CabinetResourceField,
    CabinetResourceListColumn,
    CabinetResourceRegistry,
    SmartCreateJobRef,
    SmartCreateLanguageState,
    SmartCreateStatus,
    build_resource_form_class,
    cabinet_resource_registry,
)

pytestmark = [pytest.mark.unit, pytest.mark.django_db(transaction=True)]


urlpatterns = [path("cabinet/", include("codex_django.cabinet.urls"))]


class ResourceItem(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(blank=True)
    category = models.CharField(max_length=80, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    published = models.BooleanField(default=False)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = "codex_cabinet"
        db_table = "test_cabinet_resource_item"


@dataclass(frozen=True)
class ResourceRowDto:
    id: int
    name: str
    category_name: str
    price: str
    duration: int


def list_resource_rows_for_test(request: Any, resource: CabinetResource) -> list[ResourceRowDto]:
    return [
        ResourceRowDto(
            id=item.pk,
            name=item.name,
            category_name=f"{item.category} category",
            price=f"{item.price} USD",
            duration=item.duration,
        )
        for item in resource.model.objects.order_by("name")
    ]


@pytest.fixture
def resource_table():
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(ResourceItem)
    yield
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(ResourceItem)


@pytest.fixture
def resource() -> CabinetResource:
    return CabinetResource(
        key=f"catalog.service.{uuid.uuid4().hex}",
        model=ResourceItem,
        section="Catalog",
        title="Services",
        singular_title="Service",
        list_columns=[
            CabinetResourceListColumn("name", label="Service", searchable=True),
            CabinetResourceListColumn("category", label="Category"),
            "price",
            "duration",
        ],
        form_fields=[
            CabinetResourceField(
                "name",
                label="Name",
                role="title",
                tooltip="Main editor-facing name. It is used for the list title and can be translated later.",
            ),
            "slug",
            "category",
            "price",
            "duration",
            CabinetResourceField("description", role="body", format="html"),
            "published",
        ],
        create_label="Add service",
        permissions={"list": "", "create": "", "edit": "", "publish": ""},
    )


def test_registry_registration_validation_and_helpers(resource: CabinetResource):
    registry = CabinetResourceRegistry()

    registry.register(resource)

    assert registry.get(resource.key) is resource
    assert registry.all() == [resource]
    assert registry.by_section("Catalog") == [resource]
    assert registry.registered_keys() == [resource.key]
    with pytest.raises(Exception, match="unique"):
        registry.register(resource)
    with pytest.raises(Exception, match="form field 'missing'"):
        registry.register(
            CabinetResource(
                key=f"bad.{uuid.uuid4().hex}",
                model=ResourceItem,
                section="Catalog",
                title="Bad",
                form_fields=[CabinetResourceField("missing")],
            )
        )


def test_registry_allows_selector_backed_virtual_list_columns_without_marking_virtual():
    registry = CabinetResourceRegistry()
    resource = CabinetResource(
        key=f"catalog.selector.{uuid.uuid4().hex}",
        model=ResourceItem,
        section="Catalog",
        title="Services",
        list_columns=[
            CabinetResourceListColumn("name", label="Service"),
            CabinetResourceListColumn("category_name", label="Category"),
        ],
        list_selector=list_resource_rows_for_test,
    )

    registry.register(resource)

    assert registry.get(resource.key).list_columns[1].name == "category_name"


def test_dynamic_form_generation_from_model_fields(resource: CabinetResource):
    form_class = build_resource_form_class(resource)
    form = form_class()

    assert list(form.fields) == ["name", "slug", "category", "price", "duration", "description", "published"]
    assert form.fields["name"].label == "Name"
    assert (
        form.fields["name"].widget.attrs["data-cab-field-tooltip"]
        == "Main editor-facing name. It is used for the list title and can be translated later."
    )
    assert form.fields["description"].widget.__class__.__name__ == "Textarea"
    assert form.fields["published"].widget.__class__.__name__ == "CheckboxInput"
    assert form.fields["price"].required is True


@override_settings(ROOT_URLCONF=__name__)
def test_create_button_url_context_appears(resource: CabinetResource, resource_table):
    ResourceItem.objects.create(name="Cut", price="10.00", duration=30)
    cabinet_resource_registry.register(resource)
    from codex_django.cabinet.resources.selectors import build_resource_list_context

    request = type(
        "Request",
        (),
        {
            "GET": {},
            "path": "/cabinet/resources/test/",
            "user": type("User", (), {"has_perm": lambda self, perm: True})(),
        },
    )()
    context = build_resource_list_context(request, resource)

    assert context["btn_label"] == "Add service"
    assert context["btn_url"] == reverse("resource_create", kwargs={"resource_key": resource.key})
    assert context["table"].search_param == "q"
    assert context["table"].search_action == "/cabinet/resources/test/"
    assert context["table"].search_placeholder == "Search services..."
    assert context["table"].rows[0]["name"] == "Cut"
    assert context["table"].rows[0]["edit_url"] == reverse(
        "resource_edit", kwargs={"resource_key": resource.key, "pk": 1}
    )


@override_settings(ROOT_URLCONF=__name__)
def test_list_selector_supplies_rows_while_library_builds_table_contract(resource_table):
    ResourceItem.objects.create(name="Cut", category="Hair", price="10.00", duration=30)
    resource = CabinetResource(
        key=f"catalog.selector.{uuid.uuid4().hex}",
        model=ResourceItem,
        section="Catalog",
        title="Services",
        singular_title="Service",
        list_columns=[
            CabinetResourceListColumn("name", label="Service"),
            CabinetResourceListColumn("category_name", label="Category"),
            CabinetResourceListColumn("price", label="Price"),
            CabinetResourceListColumn("duration", label="Duration"),
        ],
        list_selector=f"{__name__}.list_resource_rows_for_test",
        permissions={"list": "", "create": "", "edit": ""},
    )
    cabinet_resource_registry.register(resource)
    from codex_django.cabinet.resources.selectors import build_resource_list_context

    request = type("Request", (), {"user": type("User", (), {"has_perm": lambda self, perm: True})()})()
    context = build_resource_list_context(request, resource)

    assert [column.label for column in context["table"].columns] == ["Service", "Category", "Price", "Duration"]
    assert context["table"].rows == [
        {
            "id": 1,
            "name": "Cut",
            "category_name": "Hair category",
            "price": "10.00 USD",
            "duration": "30",
            "edit_url": reverse("resource_edit", kwargs={"resource_key": resource.key, "pk": 1}),
        }
    ]
    assert context["table"].actions[0].url_key == "edit_url"


@override_settings(ROOT_URLCONF=__name__)
def test_default_list_search_filters_rows_by_searchable_columns(resource: CabinetResource, resource_table):
    ResourceItem.objects.create(name="Cut", category="Hair", price="10.00", duration=30)
    ResourceItem.objects.create(name="Massage", category="Spa", price="42.00", duration=60)
    cabinet_resource_registry.register(resource)
    from codex_django.cabinet.resources.selectors import build_resource_list_context

    request = type(
        "Request",
        (),
        {
            "GET": {"q": "mass"},
            "path": "/cabinet/resources/test/",
            "user": type("User", (), {"has_perm": lambda self, perm: True})(),
        },
    )()
    context = build_resource_list_context(request, resource)

    assert context["table"].search_query == "mass"
    assert [row["name"] for row in context["table"].rows] == ["Massage"]


@override_settings(ROOT_URLCONF=__name__)
def test_default_list_formats_common_python_values(resource_table):
    updated_at = timezone.make_aware(datetime(2026, 5, 1, 19, 40, 42))
    ResourceItem.objects.create(name="Cut", price="10.00", duration=30, published=True, updated_at=updated_at)
    resource = CabinetResource(
        key=f"catalog.formatted.{uuid.uuid4().hex}",
        model=ResourceItem,
        section="Catalog",
        title="Services",
        list_columns=["name", "published", "updated_at"],
        permissions={"list": "", "create": "", "edit": ""},
    )
    cabinet_resource_registry.register(resource)
    from codex_django.cabinet.resources.selectors import build_resource_list_context

    request = type("Request", (), {"user": type("User", (), {"has_perm": lambda self, perm: True})()})()
    row = build_resource_list_context(request, resource)["table"].rows[0]

    assert row["published"] == "Yes"
    assert row["updated_at"] == formats.date_format(timezone.localtime(updated_at), "SHORT_DATETIME_FORMAT")


@override_settings(ROOT_URLCONF=__name__, STATIC_URL="/static/")
def test_resource_form_renders_field_tooltip(client, django_user_model, resource: CabinetResource, resource_table):
    user = django_user_model.objects.create_user("staff-tooltip", password="x")
    client.force_login(user)
    cabinet_resource_registry.register(resource)

    response = client.get(reverse("resource_create", kwargs={"resource_key": resource.key}))

    assert response.status_code == 200
    assert b"data-tippy-content" in response.content
    assert b"Main editor-facing name." in response.content
    assert b"popper.min.js" in response.content
    assert b"tippy-bundle.umd.min.js" in response.content


@override_settings(ROOT_URLCONF=__name__)
def test_normal_create_saves_model(client, django_user_model, resource: CabinetResource, resource_table):
    user = django_user_model.objects.create_user("staff-create", password="x")
    client.force_login(user)
    cabinet_resource_registry.register(resource)

    response = client.post(
        reverse("resource_create", kwargs={"resource_key": resource.key}),
        data={
            "name": "Massage",
            "slug": "massage",
            "category": "Spa",
            "price": "42.00",
            "duration": "60",
            "description": "Body work",
            "published": "on",
        },
    )

    assert response.status_code == 302
    item = ResourceItem.objects.get()
    assert item.name == "Massage"
    assert item.published is True


@override_settings(ROOT_URLCONF=__name__)
def test_edit_saves_model(client, django_user_model, resource: CabinetResource, resource_table):
    user = django_user_model.objects.create_user("staff-edit", password="x")
    client.force_login(user)
    cabinet_resource_registry.register(resource)
    item = ResourceItem.objects.create(name="Old", price="12.00", duration=45)

    response = client.post(
        reverse("resource_edit", kwargs={"resource_key": resource.key, "pk": item.pk}),
        data={
            "name": "New",
            "slug": "new",
            "category": "Spa",
            "price": "15.00",
            "duration": "50",
            "description": "Updated",
        },
    )

    assert response.status_code == 302
    item.refresh_from_db()
    assert item.name == "New"
    assert item.duration == 50


class FakeSmartHandler:
    calls: list[tuple[str, Any]] = []

    def create_preview_job(self, **kwargs: Any) -> SmartCreateJobRef:
        self.calls.append(("preview", kwargs["source_payload"]))
        return SmartCreateJobRef(draft_id="draft-1")

    def get_preview_status(self, **kwargs: Any) -> SmartCreateStatus:
        self.calls.append(("status", kwargs["draft_id"]))
        return SmartCreateStatus(
            draft_id="draft-1",
            status="ready",
            languages=[
                SmartCreateLanguageState(language="ru", status="done", fields={"name": "AI name"}),
            ],
        )

    def publish(self, **kwargs: Any) -> ResourceItem:
        self.calls.append(("publish", kwargs["edited_payload"]))
        return ResourceItem.objects.create(name="Published", price="20.00", duration=30)


@override_settings(ROOT_URLCONF=__name__)
def test_smart_create_calls_handler_and_returns_job_status_publish(
    client,
    django_user_model,
    resource_table,
):
    FakeSmartHandler.calls = []
    user = django_user_model.objects.create_user("staff-smart", password="x")
    client.force_login(user)
    resource = CabinetResource(
        key=f"content.page.{uuid.uuid4().hex}",
        model=ResourceItem,
        section="Content",
        title="Pages",
        form_fields=["name", "price", "duration"],
        smart_create=True,
        smart_handler=FakeSmartHandler,
        base_language="ru",
        target_languages=("en",),
        permissions={"list": "", "create": "", "edit": "", "publish": ""},
    )
    cabinet_resource_registry.register(resource)

    preview = client.post(
        reverse("resource_smart_preview", kwargs={"resource_key": resource.key}),
        data={"name": "Source", "price": "10.00", "duration": "30"},
    )
    status = client.get(reverse("resource_smart_status", kwargs={"resource_key": resource.key, "draft_id": "draft-1"}))
    publish = client.post(
        reverse("resource_smart_publish", kwargs={"resource_key": resource.key, "draft_id": "draft-1"}),
        data='{"languages.ru.name": "Edited"}',
        content_type="application/json",
    )

    assert preview.status_code == 200
    assert preview.json()["draft_id"] == "draft-1"
    assert preview.json()["status_url"].endswith("/drafts/draft-1/status/")
    assert status.json()["languages"][0]["fields"]["name"] == "AI name"
    assert publish.json()["pk"] == ResourceItem.objects.get().pk
    assert [call[0] for call in FakeSmartHandler.calls] == ["preview", "status", "publish"]


@override_settings(ROOT_URLCONF=__name__)
def test_smart_route_errors_clearly_when_handler_missing(client, django_user_model, resource_table):
    user = django_user_model.objects.create_user("staff-smart-missing", password="x")
    client.force_login(user)
    resource = CabinetResource(
        key=f"content.page.{uuid.uuid4().hex}",
        model=ResourceItem,
        section="Content",
        title="Pages",
        form_fields=["name", "price", "duration"],
        smart_create=True,
        permissions={"list": "", "create": "", "edit": "", "publish": ""},
    )
    cabinet_resource_registry.register(resource)

    response = client.post(
        reverse("resource_smart_preview", kwargs={"resource_key": resource.key}),
        data={"name": "Source", "price": "10.00", "duration": "30"},
    )

    assert response.status_code == 500
    assert "no smart_handler is configured" in response.json()["error"]


def test_resource_helpers_reject_unexpected_selector_and_payload_types():
    from codex_django.cabinet.resources.selectors import _row_from_selector_item
    from codex_django.cabinet.resources.services import dto_payload

    with pytest.raises(TypeError, match="dict or DTO"):
        _row_from_selector_item(object())
    with pytest.raises(TypeError, match="dataclass or dict"):
        dto_payload(object())
    with pytest.raises(TypeError, match="dataclass or dict"):
        dto_payload(SmartCreateJobRef)

    assert dto_payload({"draft_id": "one"}) == {"draft_id": "one"}
    assert dto_payload(SmartCreateJobRef(draft_id="one")) == {
        "draft_id": "one",
        "status_url": "",
        "publish_url": "",
    }


def test_resource_registry_rejects_invalid_configuration():
    from django.core.exceptions import ImproperlyConfigured

    registry = CabinetResourceRegistry()
    cases = [
        ({"key": ""}, "key must be non-empty"),
        ({"model": str}, "must be a Django Model"),
        ({"list_selector": ""}, "list_selector"),
        ({"smart_create": True}, "requires form_fields"),
        ({"list_columns": ["missing"]}, "list column 'missing'"),
    ]
    for overrides, message in cases:
        arguments = {
            "key": f"bad.{uuid.uuid4().hex}",
            "model": ResourceItem,
            "section": "Catalog",
            "title": "Bad",
            "singular_title": "Item",
        }
        arguments.update(overrides)
        with pytest.raises(ImproperlyConfigured, match=message):
            registry.register(CabinetResource(**arguments))
