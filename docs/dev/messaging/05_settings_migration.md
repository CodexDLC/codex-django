# Migrating Email Settings out of `SiteSettings`

This document is the recipe any project follows to extract email
identity + email-related URL paths out of a `SiteSettings`-style god
object into a standalone `EmailSettings` singleton subclassing
`AbstractEmailSettings`. The lily-specific application of this recipe
is in
`lily_website/docs/dev/messaging_migration/02_settings_extraction.md`.

## Why split

Today (lily) `SiteSettings` carries 30+ fields covering: company
identity, contact info, geo, marketing analytics, technical scripts,
social URLs, AND email identity. Every consumer of email config
imports the whole god object. A focused `EmailSettings` model:

* Reduces the surface that an "email" change touches.
* Lets the messaging cabinet have its own settings page (mirroring
  booking).
* Makes it possible to ship `AbstractEmailSettings` as a reusable
  mixin in `codex-django` so other projects don't reinvent the schema.

## Field inventory

Move out of `SiteSettings`:

| Field | Why it's email-related |
|-------|-----------------------|
| `email_from` | "From:" header. |
| `email_sender_name` | "From:" display name. |
| `email_reply_to` | "Reply-To:" header. |
| `site_base_url` | Used in every email body to build links back. |
| `logo_url` | Embedded in every email template. |
| `url_path_confirm` | Booking confirm CTA URL fragment. |
| `url_path_cancel` | Booking cancel CTA URL fragment. |
| `url_path_reschedule` | Booking reschedule CTA URL fragment. |
| `url_path_contact_form` | Contact form receipt URL fragment. |

Fields that **stay** in `SiteSettings`:

* `company_name`, `owner_name`, `tax_number`
* `phone`, `email` (contact email — not the from-address!),
  `address_*`, `contact_person`
* All social/analytics/marketing/technical fields
* `working_hours_*`, `price_range`, `app_mode_enabled`,
  `maintenance_mode`

## Discussion: why `site_base_url` and `logo_url` move with email

These two fields are shared between branding (used on the website
chrome) and email composition. Two options:

1. **Duplicate**: keep on `SiteSettings` for the website, copy to
   `EmailSettings` for emails. Drift risk if someone updates one and
   forgets the other.
2. **Move**: emails are the dominant consumer (~10 templates each
   reads them; the website itself reads them once at the layout
   level). Move them to `EmailSettings` and have the website read
   from there too.

We recommend **option 2 — move**. The site-base URL and logo URL are
properties of the email-as-product more than of the marketing site.
The website is a single template; making it read from `EmailSettings`
is one line.

## Migration steps

### Step 1 — define the abstract mixin

In `codex-django`:

```python
# src/codex_django/messaging/mixins/settings.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractEmailSettings(models.Model):
    email_from        = models.EmailField(_("From address"))
    email_sender_name = models.CharField(_("Sender name"), max_length=128)
    email_reply_to    = models.EmailField(_("Reply-To"), blank=True)

    site_base_url     = models.URLField(_("Site base URL"))
    logo_url          = models.CharField(_("Logo URL"), max_length=255, blank=True)

    url_path_confirm      = models.CharField(_("Confirm URL path"), max_length=255, blank=True)
    url_path_cancel       = models.CharField(_("Cancel URL path"), max_length=255, blank=True)
    url_path_reschedule   = models.CharField(_("Reschedule URL path"), max_length=255, blank=True)
    url_path_contact_form = models.CharField(_("Contact form URL path"), max_length=255, blank=True)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        abstract = True
```

### Step 2 — define the concrete project model

In the project (e.g. lily):

```python
# src/lily_backend/features/messaging/messaging_settings.py
from codex_django.messaging.mixins import AbstractEmailSettings, EmailSettingsSyncMixin


class EmailSettings(AbstractEmailSettings, EmailSettingsSyncMixin):
    class Meta:
        verbose_name = "Email Settings"
        verbose_name_plural = "Email Settings"
```

`EmailSettingsSyncMixin` (next section) hooks `post_save` to sync to
Redis.

### Step 3 — Redis sync mixin

`EmailSettingsSyncMixin` lives in `codex_django.messaging.mixins.sync`.
It hooks `post_save` and pushes the singleton's fields into the Redis
hash named in `messaging.workers_contract.SETTINGS_HASH_KEY` (default:
`"email_settings:"`).

```python
class EmailSettingsSyncMixin:
    """Sync the singleton to Redis on every save."""

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from codex_django.messaging.adapters import EmailSettingsRedisManager
        EmailSettingsRedisManager().sync(self)
```

The mirror of this in the worker (`merge_email_settings()` in
`src/workers/core/site_settings.py:62-79`) is renamed
`merge_email_settings` and reads from the same hash. Today the same
function reads from `site_settings:` — the rename is the migration's
naming alignment.

### Step 4 — data migration

Django data migration (one-shot):

```python
# 0042_extract_email_settings.py
from django.db import migrations


def copy_to_email_settings(apps, schema_editor):
    SiteSettings  = apps.get_model("system", "SiteSettings")
    EmailSettings = apps.get_model("messaging", "EmailSettings")

    site = SiteSettings.objects.filter(pk=1).first()
    if site is None:
        return

    EmailSettings.objects.update_or_create(
        pk=1,
        defaults={
            "email_from":             getattr(site, "email_from", ""),
            "email_sender_name":      getattr(site, "email_sender_name", ""),
            "email_reply_to":         getattr(site, "email_reply_to", ""),
            "site_base_url":          getattr(site, "site_base_url", ""),
            "logo_url":               getattr(site, "logo_url", ""),
            "url_path_confirm":       getattr(site, "url_path_confirm", ""),
            "url_path_cancel":        getattr(site, "url_path_cancel", ""),
            "url_path_reschedule":    getattr(site, "url_path_reschedule", ""),
            "url_path_contact_form":  getattr(site, "url_path_contact_form", ""),
        },
    )


class Migration(migrations.Migration):
    dependencies = [...]
    operations = [
        migrations.RunPython(copy_to_email_settings, migrations.RunPython.noop),
    ]
```

A second migration removes the now-empty fields from `SiteSettings`:

```python
class Migration(migrations.Migration):
    dependencies = [...]
    operations = [
        migrations.RemoveField("system", "siteemailidentitymixin", "email_from"),
        # … etc.
        # Remove SiteEmailIdentityMixin from SiteSettings's bases
    ]
```

### Step 5 — update consumers

Every place that reads `SiteSettings.load().email_*` or
`.site_base_url` / `.logo_url` / `.url_path_*` switches to
`EmailSettings.load().…`.

Use `grep` to find them:

```
grep -rn "SiteSettings" src/lily_backend/ | \
    grep -E "\.(email_|url_path_|site_base_url|logo_url)"
```

### Step 6 — worker config rename

Rename the Redis hash key from `site_settings:` to `email_settings:`
in:

* `src/workers/core/site_settings.py` (worker side reader)
* `codex_django.notifications.adapters.SiteSettingsRedisManager` (or
  wherever the Django writer lives)

The migration runs through a deprecation window: the writer writes to
**both** keys for one minor release; the reader prefers the new key
and falls back to the old one. After deprecation, only the new key
is used.

## Field type aliases (for project flexibility)

Some projects may want to override field types — e.g. a project that
has a more granular logo asset reference might want `logo_url` to be a
FK to a Media model. Two options:

1. Override the field on the concrete subclass:
   ```python
   class EmailSettings(AbstractEmailSettings):
       logo_url = models.ForeignKey("media.Asset", on_delete=models.PROTECT)
   ```
   Django handles this — the abstract field is just shadowed.

2. Keep `logo_url` as `CharField` and resolve to the asset via a
   computed property. Recommended unless a project genuinely needs
   referential integrity on the asset.

## Anti-patterns

* **Adding `smtp_host` to `EmailSettings`.** SMTP credentials stay in
  env. The migration deliberately resists adding them to keep the
  invariant that secrets never end up in DB.
* **Reading `EmailSettings.load()` from inside a worker.** The worker
  reads from Redis. Direct ORM access from a worker would re-couple
  the worker to Django.
* **Skipping the data migration.** Running step 5 before step 4 means
  consumers will read from an empty `EmailSettings` while the data
  still lives in `SiteSettings`. Order matters.
