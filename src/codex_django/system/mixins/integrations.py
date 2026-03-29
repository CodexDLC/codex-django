"""Integration mixins for storing provider credentials in site settings models.

Compose these mixins with :class:`codex_django.system.mixins.settings.AbstractSiteSettings`
to keep third-party credentials in a single singleton-like settings object.
Each mixin documents the Django admin wiring that should be added when the
fields are exposed in the project's ``ModelAdmin``.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_model_fields.fields import EncryptedCharField


class GoogleIntegrationsMixin(models.Model):
    """Add Google Maps, Business, and reCAPTCHA credentials.

    Notes:
        Secret values that should not be exposed publicly are stored in
        encrypted fields where appropriate.

    Admin:
        fieldsets: (
            _("Google Services"),
            {
                "fields": (
                    "google_maps_api_key",
                    "google_business_api_key",
                    "google_recaptcha_site_key",
                    "google_recaptcha_secret_key",
                ),
                "classes": ("collapse",),
            },
        )
    """

    google_maps_api_key = models.CharField(_("Google Maps API Key"), max_length=255, blank=True)
    google_business_api_key = models.CharField(_("Google Business API Key"), max_length=255, blank=True)
    google_recaptcha_site_key = models.CharField(_("reCAPTCHA Site Key"), max_length=255, blank=True)
    google_recaptcha_secret_key = EncryptedCharField(_("reCAPTCHA Secret Key"), max_length=255, blank=True)

    class Meta:
        abstract = True


class MetaIntegrationsMixin(models.Model):
    """Add Meta platform credentials for Facebook and Instagram integrations.

    Notes:
        This mixin is aimed at ad pixels and app-level integrations rather
        than content embeds.

    Admin:
        fieldsets: (
            _("Meta (Facebook/Instagram)"),
            {
                "fields": ("facebook_pixel_id", "facebook_app_id", "facebook_app_secret"),
                "classes": ("collapse",),
            },
        )
    """

    facebook_pixel_id = models.CharField(_("Facebook Pixel ID"), max_length=255, blank=True)
    facebook_app_id = models.CharField(_("Facebook App ID"), max_length=255, blank=True)
    facebook_app_secret = EncryptedCharField(_("Facebook App Secret"), max_length=255, blank=True)

    class Meta:
        abstract = True


class StripeIntegrationsMixin(models.Model):
    """Add Stripe payment credentials and webhook secrets.

    Notes:
        The secret and webhook fields use encrypted storage because they are
        server-side credentials.

    Admin:
        fieldsets: (
            _("Stripe Payments"),
            {
                "fields": ("stripe_public_key", "stripe_secret_key", "stripe_webhook_secret"),
                "classes": ("collapse",),
            },
        )
    """

    stripe_public_key = models.CharField(_("Stripe Public Key"), max_length=255, blank=True)
    stripe_secret_key = EncryptedCharField(_("Stripe Secret Key"), max_length=255, blank=True)
    stripe_webhook_secret = EncryptedCharField(_("Stripe Webhook Secret"), max_length=255, blank=True)

    class Meta:
        abstract = True


class CrmIntegrationsMixin(models.Model):
    """Add a generic CRM endpoint and API key pair.

    Notes:
        This mixin intentionally stays provider-agnostic so projects can wire
        custom CRM clients around a simple URL + credential contract.

    Admin:
        fieldsets:
            (_("CRM Integration"), {"fields": ("crm_api_url", "crm_api_key"), "classes": ("collapse",)})
    """

    crm_api_url = models.URLField(_("CRM API URL"), blank=True)
    crm_api_key = EncryptedCharField(_("CRM API Key"), max_length=255, blank=True)

    class Meta:
        abstract = True


class TwilioIntegrationsMixin(models.Model):
    """Add Twilio credentials for SMS and WhatsApp delivery.

    Notes:
        The mixin stores both SMS and WhatsApp sender configuration because
        projects often enable them together.

    Admin:
        fieldsets: (
            _("Twilio (SMS / WhatsApp)"),
            {
                "fields": (
                    "twilio_account_sid",
                    "twilio_auth_token",
                    "twilio_from_number",
                    "twilio_whatsapp_from",
                ),
                "classes": ("collapse",),
            },
        )
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
    """Add Seven.io credentials for SMS and WhatsApp delivery.

    Notes:
        Use this mixin as a lightweight alternative to Twilio when Seven.io
        is the preferred outbound provider.

    Admin:
        fieldsets:
            (_("Seven.io (SMS / WhatsApp)"), {"fields": ("seven_api_key", "seven_sender_id"), "classes": ("collapse",)})
    """

    seven_api_key = EncryptedCharField(_("Seven.io API Key"), max_length=255, blank=True)
    seven_sender_id = models.CharField(
        _("Seven.io Sender ID"), max_length=50, blank=True, help_text=_("SMS sender name or number")
    )

    class Meta:
        abstract = True


class ExtraIntegrationsMixin(models.Model):
    """Add a JSON field for custom or project-specific integration settings.

    Notes:
        This field is best used as an extension point for values that do not
        justify a dedicated strongly typed mixin yet.

    Admin:
        fieldsets:
            (_("Extra Integrations"), {"fields": ("extra_config",), "classes": ("collapse",)})
    """

    extra_config = models.JSONField(_("Extra Configuration"), default=dict, blank=True)

    class Meta:
        abstract = True
