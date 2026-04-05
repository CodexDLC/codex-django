"""Reusable mixins for building a project-specific site settings model.

Combine :class:`AbstractSiteSettings` with the desired field mixins inside the
target project's ``system`` app, then point
``settings.CODEX_SITE_SETTINGS_MODEL`` to the concrete model. Instances are
serialized to Redis automatically through :class:`SiteSettingsSyncMixin`.
"""

from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_lifecycle import AFTER_SAVE, LifecycleModelMixin, hook

from codex_django.core.redis.managers.settings import DjangoSiteSettingsManager


class SiteSettingsSyncMixin(LifecycleModelMixin, models.Model):
    """Provide Redis synchronization helpers for site settings models.

    Notes:
        Projects usually do not instantiate this mixin directly. Instead it
        is inherited through :class:`AbstractSiteSettings`.
    """

    class Meta:
        abstract = True

    # Redis manager class used for sync
    redis_manager_class = DjangoSiteSettingsManager

    def to_dict(self) -> dict[str, Any]:
        """Serialize concrete model fields into a Redis-friendly mapping.

        Returns:
            A dictionary containing concrete non-relational field values.
            File fields are converted to their public URL when available.
        """
        data: dict[str, Any] = {}
        for field in self._meta.get_fields():
            if field.concrete and not field.many_to_many and not field.one_to_many:
                if field.name in ["id", "pk"]:
                    continue

                value = getattr(self, field.name)
                # Handle files (store the URL)
                if isinstance(field, models.FileField) and value:
                    try:
                        data[field.name] = value.url
                    except ValueError:
                        data[field.name] = None
                else:
                    data[field.name] = value
        return data

    @hook(AFTER_SAVE)  # type: ignore[untyped-decorator]
    def sync_to_redis(self) -> None:
        """Hook to automatically update Redis cache upon saving.

        In DEBUG mode Redis sync is skipped unless CODEX_REDIS_ENABLED=True.
        This allows local development without a running Redis instance.
        """
        from django.conf import settings

        if settings.DEBUG and not getattr(settings, "CODEX_REDIS_ENABLED", False):
            return

        from codex_django.core.redis.managers.settings import get_site_settings_manager

        manager = get_site_settings_manager()
        manager.save_instance(self)


class SiteContactSettingsMixin(models.Model):
    """Add contact information fields to a site settings model.

    Notes:
        Use this mixin when the project needs a single editable source for
        phone, email, address, and public contact metadata.

    Admin:
        fieldsets: (
            _("Contact Information"),
            {
                "fields": (
                    "phone",
                    "email",
                    "address_street",
                    "address_locality",
                    "address_postal_code",
                    "contact_person",
                    "working_hours",
                ),
            },
        )
    """

    phone = models.CharField(_("Phone"), max_length=50, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    address_street = models.CharField(_("Street Address"), max_length=255, blank=True)
    address_locality = models.CharField(_("City/Locality"), max_length=255, blank=True)
    address_postal_code = models.CharField(_("Postal Code"), max_length=10, blank=True)

    contact_person = models.CharField(_("Contact Person"), max_length=255, blank=True)
    working_hours = models.TextField(_("Working Hours"), blank=True)

    class Meta:
        abstract = True


class SiteGeoSettingsMixin(models.Model):
    """Add map and geographic metadata fields to a site settings model.

    Notes:
        These fields are useful for map embeds, structured data, and contact
        pages that need coordinates or provider links.

    Admin:
        fieldsets:
            (_("Geography & Map"), {"fields": ("google_maps_link", "latitude", "longitude"), "classes": ("collapse",)})
    """

    google_maps_link = models.URLField(_("Google Maps Link"), blank=True, max_length=500)
    latitude = models.CharField(_("Latitude"), max_length=50, blank=True)
    longitude = models.CharField(_("Longitude"), max_length=50, blank=True)

    class Meta:
        abstract = True


class SiteSocialSettingsMixin(models.Model):
    """Add social network URL fields to a site settings model.

    Notes:
        The mixin is intentionally broad so projects can expose only the
        subset of networks they actually render in templates.

    Admin:
        fieldsets: (
            _("Social Networks"),
            {
                "fields": (
                    "instagram_url",
                    "facebook_url",
                    "telegram_url",
                    "whatsapp_url",
                    "youtube_url",
                    "linkedin_url",
                    "tiktok_url",
                    "twitter_url",
                    "pinterest_url",
                ),
                "classes": ("collapse",),
            },
        )
    """

    instagram_url = models.URLField(_("Instagram URL"), blank=True)
    facebook_url = models.URLField(_("Facebook URL"), blank=True)
    telegram_url = models.URLField(_("Telegram URL"), blank=True)
    whatsapp_url = models.URLField(_("WhatsApp URL"), blank=True)
    youtube_url = models.URLField(_("YouTube URL"), blank=True)
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True)
    tiktok_url = models.URLField(_("TikTok URL"), blank=True)
    twitter_url = models.URLField(_("Twitter (X) URL"), blank=True)
    pinterest_url = models.URLField(_("Pinterest URL"), blank=True)

    class Meta:
        abstract = True


class SiteMarketingSettingsMixin(models.Model):
    """Add analytics and marketing tracking identifiers.

    Notes:
        These values are typically consumed by template includes that inject
        analytics and pixel scripts conditionally.

    Admin:
        fieldsets: (
            _("Marketing & Analytics"),
            {
                "fields": (
                    "google_analytics_id",
                    "google_tag_manager_id",
                    "facebook_pixel_id",
                    "tiktok_pixel_id",
                ),
                "classes": ("collapse",),
            },
        )
    """

    google_analytics_id = models.CharField(_("Google Analytics ID"), max_length=50, blank=True)
    google_tag_manager_id = models.CharField(_("Google Tag Manager ID"), max_length=50, blank=True)
    facebook_pixel_id = models.CharField(_("Facebook Pixel ID"), max_length=50, blank=True)
    tiktok_pixel_id = models.CharField(_("TikTok Pixel ID"), max_length=50, blank=True)

    class Meta:
        abstract = True


class SiteTechnicalSettingsMixin(models.Model):
    """Add operational flags and raw script injection fields.

    Notes:
        This mixin is aimed at operational toggles and controlled script
        injection, not arbitrary long-form content storage.

    Admin:
        fieldsets: (
            _("Technical Settings"),
            {
                "fields": ("app_mode_enabled", "maintenance_mode", "head_scripts", "body_scripts"),
                "classes": ("collapse",),
            },
        )
    """

    app_mode_enabled = models.BooleanField(_("App Mode Enabled"), default=False)
    maintenance_mode = models.BooleanField(_("Maintenance Mode"), default=False)
    head_scripts = models.TextField(_("Scripts in <head>"), blank=True)
    body_scripts = models.TextField(_("Scripts in <body>"), blank=True)

    class Meta:
        abstract = True


class SiteEmailSettingsMixin(models.Model):
    """Add SMTP and email provider configuration fields.

    Notes:
        These fields allow small projects to keep delivery configuration in a
        single singleton-like settings model.

    Admin:
        fieldsets: (
            _("Email Source Settings (SMTP)"),
            {
                "fields": (
                    "smtp_host",
                    "smtp_port",
                    "smtp_user",
                    "smtp_password",
                    "smtp_from_email",
                    "smtp_use_tls",
                    "smtp_use_ssl",
                    "sendgrid_api_key",
                ),
                "classes": ("collapse",),
            },
        )
    """

    smtp_host = models.CharField(_("SMTP Host"), max_length=255, blank=True)
    smtp_port = models.IntegerField(_("SMTP Port"), default=465)
    smtp_user = models.CharField(_("SMTP User"), max_length=255, blank=True)
    smtp_password = models.CharField(_("SMTP Password"), max_length=255, blank=True)
    smtp_from_email = models.EmailField(_("SMTP From Email"), blank=True)
    smtp_use_tls = models.BooleanField(_("Use TLS"), default=True)
    smtp_use_ssl = models.BooleanField(_("Use SSL"), default=False)

    sendgrid_api_key = models.CharField(_("SendGrid API Key"), max_length=255, blank=True)

    class Meta:
        abstract = True


class AbstractSiteSettings(SiteSettingsSyncMixin, models.Model):
    """Base abstract site settings model with Redis synchronization only.

    Notes:
        Subclass this model and compose it with the field mixins from this
        module to build the concrete settings model for a project.

    Admin:
        Typically registered as a singleton-like model combined with the
        desired fieldset groups from the selected mixins.
    """

    class Meta:
        abstract = True
