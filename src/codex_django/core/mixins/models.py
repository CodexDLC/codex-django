import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampMixin(models.Model):
    """
    Adds created_at and updated_at fields.

    Admin fieldsets example (usually read-only):
    --------------------------------------------
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    """

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    """
    Adds is_active field for visibility control.

    Admin fieldsets example:
    ------------------------
        (_("Status"), {
            "fields": ("is_active",),
        }),
    """

    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("If unchecked, the object will be hidden on the site."),
    )

    class Meta:
        abstract = True


class SeoMixin(models.Model):
    """
    Adds SEO fields (title, description, OG Image).

    Admin fieldsets example:
    ------------------------
        (_("SEO Settings"), {
            "fields": ("seo_title", "seo_description", "seo_image"),
            "classes": ("collapse",)
        }),
    """

    seo_title = models.CharField(_("SEO Title"), max_length=255, blank=True)
    seo_description = models.TextField(_("SEO Description"), blank=True)
    seo_image = models.ImageField(_("OG Image"), upload_to="seo/", blank=True, null=True)

    class Meta:
        abstract = True


class OrderableMixin(models.Model):
    """
    Adds a generic 'order' field for custom sorting.

    Admin fieldsets example:
    ------------------------
        (_("Ordering"), {
            "fields": ("order",),
        }),
    """

    order = models.PositiveIntegerField(_("Sorting Order"), default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ["order"]


class SoftDeleteMixin(models.Model):
    """
    Adds 'is_deleted' flag to prevent data loss on deletion.

    Admin fieldsets example:
    ------------------------
        (_("Archive / Deletion"), {
            "fields": ("is_deleted",),
            "classes": ("collapse",)
        }),
    """

    is_deleted = models.BooleanField(_("Is Deleted"), default=False)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """Soft deletes the object by setting the is_deleted flag."""
        self.is_deleted = True
        self.save()


class UUIDMixin(models.Model):
    """
    Replaces standard integer PK with a secure UUID4.

    Admin fieldsets example (usually read-only in admin!):
    ------------------------------------------------------
        (_("Identifiers"), {
            "fields": ("id",),
            "classes": ("collapse",)
        }),

        # NOTE: Make sure to add "id" to readonly_fields in ModelAdmin
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SlugMixin(models.Model):
    """
    Adds a unique 'slug' field for URLs.

    Admin fieldsets example:
    ------------------------
        (_("URL"), {
            "fields": ("slug",),
        }),

        # NOTE: You usually want to prepopulate this field in ModelAdmin:
        # prepopulated_fields = {"slug": ("title",)}  # Replace 'title' with your model's title field
    """

    slug = models.SlugField(_("URL Slug"), max_length=255, unique=True, blank=True)

    class Meta:
        abstract = True
