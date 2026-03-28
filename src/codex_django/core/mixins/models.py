"""Reusable abstract Django model mixins shared across codex-django packages.

Examples:
    Combine several mixins in a project model::

        from django.db import models
        from codex_django.core.mixins.models import TimestampMixin, ActiveMixin, SeoMixin

        class Article(TimestampMixin, ActiveMixin, SeoMixin, models.Model):
            title = models.CharField(max_length=200)
"""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampMixin(models.Model):
    """Add creation and update timestamps to a model.

    Notes:
        ``created_at`` is written once on insert, while ``updated_at`` is
        refreshed on every save.

    Admin:
        fieldsets:
            (_("Timestamps"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)})
        readonly_fields: ("created_at", "updated_at")
    """

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    """Add an ``is_active`` flag for publication and visibility control.

    Notes:
        Use this mixin when objects should remain queryable in the database
        but be hidden from public listings, navigation, or API responses.

    Admin:
        fieldsets:
            (_("Status"), {"fields": ("is_active",)})
        list_filter: ("is_active",)
    """

    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("If unchecked, the object will be hidden on the site."),
    )

    class Meta:
        abstract = True


class SeoMixin(models.Model):
    """Add basic per-object SEO fields for title, description, and OG image.

    Notes:
        This mixin is intended for content models that need per-instance
        metadata overrides in templates, cards, or sitemap-adjacent views.

    Admin:
        fieldsets:
            (_("SEO Settings"), {"fields": ("seo_title", "seo_description", "seo_image"), "classes": ("collapse",)})
    """

    seo_title = models.CharField(_("SEO Title"), max_length=255, blank=True)
    seo_description = models.TextField(_("SEO Description"), blank=True)
    seo_image = models.ImageField(_("OG Image"), upload_to="seo/", blank=True, null=True)

    class Meta:
        abstract = True


class OrderableMixin(models.Model):
    """Add a generic ``order`` field for custom manual sorting.

    Notes:
        The mixin sets ``Meta.ordering = ["order"]`` on the abstract base.

    Admin:
        fieldsets:
            (_("Ordering"), {"fields": ("order",)})
        list_display:
            include ``order`` when manual ordering should be visible in admin.
    """

    order = models.PositiveIntegerField(_("Sorting Order"), default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ["order"]


class SoftDeleteMixin(models.Model):
    """Add an ``is_deleted`` flag for soft-deletion workflows.

    Notes:
        The model instance remains in the database. Call ``soft_delete()``
        when the project wants reversible deletion semantics.

    Admin:
        fieldsets:
            (_("Archive / Deletion"), {"fields": ("is_deleted",), "classes": ("collapse",)})
        list_filter: ("is_deleted",)
    """

    is_deleted = models.BooleanField(_("Is Deleted"), default=False)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """Mark the object as deleted without removing the database row.

        Notes:
            The method updates ``is_deleted`` and immediately saves the model
            instance using the default manager behavior.
        """
        self.is_deleted = True
        self.save()


class UUIDMixin(models.Model):
    """Replace the default integer primary key with a UUID4 identifier.

    Notes:
        This mixin is useful for public-facing URLs or distributed systems
        where sequential integer identifiers should not be exposed.

    Admin:
        fieldsets:
            (_("Identifiers"), {"fields": ("id",), "classes": ("collapse",)})
        readonly_fields: ("id",)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SlugMixin(models.Model):
    """Add a unique slug field suitable for URL routing.

    Notes:
        The field is intentionally declared with ``blank=True`` so projects
        can populate it through admin prepopulation, model hooks, or custom
        save logic.

    Admin:
        fieldsets:
            (_("URL"), {"fields": ("slug",)})
        prepopulated_fields:
            {"slug": ("title",)}  # Replace ``title`` with the concrete source field.
    """

    slug = models.SlugField(_("URL Slug"), max_length=255, unique=True, blank=True)

    class Meta:
        abstract = True
