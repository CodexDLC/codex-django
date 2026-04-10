from unittest.mock import patch

import pytest
from django.db import models

from codex_django.core.mixins import (
    ActiveMixin,
    OrderableMixin,
    SeoMixin,
    SlugMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class SampleModel(
    TimestampMixin,
    ActiveMixin,
    SeoMixin,
    OrderableMixin,
    SoftDeleteMixin,
    UUIDMixin,
    SlugMixin,
    models.Model,
):
    class Meta:
        app_label = "tests"


@pytest.mark.unit
def test_core_mixins_export_expected_fields():
    field_names = {field.name for field in SampleModel._meta.fields}

    assert {
        "id",
        "created_at",
        "updated_at",
        "is_active",
        "seo_title",
        "seo_description",
        "seo_image",
        "order",
        "is_deleted",
        "slug",
    }.issubset(field_names)


@pytest.mark.unit
def test_soft_delete_marks_instance_and_saves():
    instance = SampleModel()

    with patch.object(instance, "save") as save:
        instance.soft_delete()

    assert instance.is_deleted is True
    save.assert_called_once_with()
