"""
codex_django.system.mixins.integrations
=======================================
Mixins for adding external integration API keys and secrets to Site Settings.

Usage in models.py:
-------------------
    from codex_django.system.mixins.settings import AbstractSiteSettings
    from codex_django.system.mixins.integrations import (
        GoogleIntegrationsMixin,
        StripeIntegrationsMixin,
    )

    class SiteSettings(
        AbstractSiteSettings,
        GoogleIntegrationsMixin,
        StripeIntegrationsMixin
    ):
        class Meta:
            verbose_name = "Site Settings"

Configuring Django Admin (admin.py):
------------------------------------
When using these mixins, you must expose their fields in the admin panel by
customizing the `fieldsets` in your `ModelAdmin`.

Example of adding Google and Stripe fields to the admin panel:

    from django.contrib import admin
    from django.utils.translation import gettext_lazy as _
    from .models import SiteSettings

    @admin.register(SiteSettings)
    class SiteSettingsAdmin(admin.ModelAdmin):
        def has_add_permission(self, request):
            # Enforce singleton pattern
            return not SiteSettings.objects.exists()

        fieldsets = (
            (_("Google Services"), {
                "fields": (
                    "google_maps_api_key",
                    "google_business_api_key",
                    "google_recaptcha_site_key",
                    "google_recaptcha_secret_key"
                ),
                "classes": ("collapse",)
            }),
            (_("Stripe Payments"), {
                "fields": (
                    "stripe_public_key",
                    "stripe_secret_key",
                    "stripe_webhook_secret"
                ),
                "classes": ("collapse",)
            }),
            # You can also add the generic JSON config
            (_("Extra Integrations"), {
                "fields": ("extra_config",),
                "classes": ("collapse",)
            }),
        )
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_model_fields.fields import EncryptedCharField


class GoogleIntegrationsMixin(models.Model):
    """
    Google Services API keys (Maps, Recaptcha, Business).

    Admin fieldsets example:
    ------------------------
        (_("Google Services"), {
            "fields": (
                "google_maps_api_key",
                "google_business_api_key",
                "google_recaptcha_site_key",
                "google_recaptcha_secret_key",
            ),
            "classes": ("collapse",)
        }),
    """

    google_maps_api_key = models.CharField(_("Google Maps API Key"), max_length=255, blank=True)
    google_business_api_key = models.CharField(_("Google Business API Key"), max_length=255, blank=True)
    google_recaptcha_site_key = models.CharField(_("reCAPTCHA Site Key"), max_length=255, blank=True)
    google_recaptcha_secret_key = EncryptedCharField(_("reCAPTCHA Secret Key"), max_length=255, blank=True)

    class Meta:
        abstract = True


class MetaIntegrationsMixin(models.Model):
    """
    Meta (Facebook/Instagram) credentials.

    Admin fieldsets example:
    ------------------------
        (_("Meta (Facebook/Instagram)"), {
            "fields": (
                "facebook_pixel_id",
                "facebook_app_id",
                "facebook_app_secret",
            ),
            "classes": ("collapse",)
        }),
    """

    facebook_pixel_id = models.CharField(_("Facebook Pixel ID"), max_length=255, blank=True)
    facebook_app_id = models.CharField(_("Facebook App ID"), max_length=255, blank=True)
    facebook_app_secret = EncryptedCharField(_("Facebook App Secret"), max_length=255, blank=True)

    class Meta:
        abstract = True


class StripeIntegrationsMixin(models.Model):
    """
    Stripe Payment credentials.

    Admin fieldsets example:
    ------------------------
        (_("Stripe Payments"), {
            "fields": (
                "stripe_public_key",
                "stripe_secret_key",
                "stripe_webhook_secret",
            ),
            "classes": ("collapse",)
        }),
    """

    stripe_public_key = models.CharField(_("Stripe Public Key"), max_length=255, blank=True)
    stripe_secret_key = EncryptedCharField(_("Stripe Secret Key"), max_length=255, blank=True)
    stripe_webhook_secret = EncryptedCharField(_("Stripe Webhook Secret"), max_length=255, blank=True)

    class Meta:
        abstract = True


class CrmIntegrationsMixin(models.Model):
    """
    Generic CRM connection credentials.

    Admin fieldsets example:
    ------------------------
        (_("CRM Integration"), {
            "fields": (
                "crm_api_url",
                "crm_api_key",
            ),
            "classes": ("collapse",)
        }),
    """

    crm_api_url = models.URLField(_("CRM API URL"), blank=True)
    crm_api_key = EncryptedCharField(_("CRM API Key"), max_length=255, blank=True)

    class Meta:
        abstract = True


class TwilioIntegrationsMixin(models.Model):
    """
    Twilio API credentials (SMS / WhatsApp).

    Admin fieldsets example:
    ------------------------
        (_("Twilio (SMS / WhatsApp)"), {
            "fields": (
                "twilio_account_sid",
                "twilio_auth_token",
                "twilio_from_number",
                "twilio_whatsapp_from",
            ),
            "classes": ("collapse",)
        }),
    """

    twilio_account_sid = models.CharField(_("Twilio Account SID"), max_length=255, blank=True)
    twilio_auth_token = EncryptedCharField(_("Twilio Auth Token"), max_length=255, blank=True)
    twilio_from_number = models.CharField(
        _("Twilio From Number"), max_length=50, blank=True, help_text=_("E.g. +15017122661")
    )
    twilio_whatsapp_from = models.CharField(
        _("Twilio WhatsApp From"), max_length=50, blank=True, help_text=_("E.g. +14155238886")
    )

    class Meta:
        abstract = True


class SevenIoIntegrationsMixin(models.Model):
    """
    Seven.io API credentials (SMS / WhatsApp).

    Admin fieldsets example:
    ------------------------
        (_("Seven.io (SMS / WhatsApp)"), {
            "fields": (
                "seven_api_key",
                "seven_sender_id",
            ),
            "classes": ("collapse",)
        }),
    """

    seven_api_key = EncryptedCharField(_("Seven.io API Key"), max_length=255, blank=True)
    seven_sender_id = models.CharField(
        _("Seven.io Sender ID"), max_length=50, blank=True, help_text=_("SMS sender name or number")
    )

    class Meta:
        abstract = True


class ExtraIntegrationsMixin(models.Model):
    """
    Flexible JSON field for custom or ad-hoc integrations.

    Admin fieldsets example:
    ------------------------
        (_("Extra Integrations"), {
            "fields": ("extra_config",),
            "classes": ("collapse",)
        }),
    """

    extra_config = models.JSONField(_("Extra Configuration"), default=dict, blank=True)

    class Meta:
        abstract = True
