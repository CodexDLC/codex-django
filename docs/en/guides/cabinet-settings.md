# Site Settings

The settings module in the cabinet is built on dynamic blocks (partials). This allows for easy expansion of the standard set of fields or complete replacement of standard blocks at the project level.

## How it works

All settings blocks are loaded automatically from the `cabinet/site_settings/partials/` folder.
If a file with the same name exists in your project, Django will prioritize your project's version over the library version.

---

## Standard Blocks Reference

Below is the source code of all standard blocks provided by the `codex-django` library. You can use this code as a base for your own customization.

### 1. Contacts (`_contact.html`)
Contains fields: phone, email, contact person, working hours, and address.

<details>
<summary>Show template code</summary>

```html
{% load i18n %}
<div class="row g-4">
  <div class="col-12">

    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white border-0 pt-3 pb-0">
        <h6 class="fw-semibold mb-0">Контактная информация</h6>
      </div>
      <div class="card-body d-flex flex-column gap-3">

        <div class="row align-items-center">
          <div class="col-sm-4">
            <label class="form-label text-muted mb-0" style="font-size:.8rem;">Телефон</label>
          </div>
          <div class="col-sm-8">
            <input type="text" name="phone" value="{{ settings_data.phone|default:'' }}"
                   class="form-control form-control-sm border-0 bg-light" placeholder="+7 (000) 000-00-00">
          </div>
        </div>

        <div class="row align-items-center">
          <div class="col-sm-4">
            <label class="form-label text-muted mb-0" style="font-size:.8rem;">Email</label>
          </div>
          <div class="col-sm-8">
            <input type="email" name="email" value="{{ settings_data.email|default:'' }}"
                   class="form-control form-control-sm border-0 bg-light" placeholder="info@example.com">
          </div>
        </div>

        <div class="row align-items-center">
          <div class="col-sm-4">
            <label class="form-label text-muted mb-0" style="font-size:.8rem;">Контактное лицо</label>
          </div>
          <div class="col-sm-8">
            <input type="text" name="contact_person" value="{{ settings_data.contact_person|default:'' }}"
                   class="form-control form-control-sm border-0 bg-light">
          </div>
        </div>

        <div>
          <label class="form-label text-muted mb-1" style="font-size:.8rem;">Часы работы</label>
          <textarea name="working_hours" rows="2"
                    class="form-control form-control-sm border-0 bg-light">{{ settings_data.working_hours|default:'' }}</textarea>
        </div>

      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-0 pt-3 pb-0">
        <h6 class="fw-semibold mb-0">Адрес</h6>
      </div>
      <div class="card-body d-flex flex-column gap-3">

        <div>
          <label class="form-label text-muted mb-1" style="font-size:.8rem;">Улица и дом</label>
          <input type="text" name="address_street" value="{{ settings_data.address_street|default:'' }}"
                 class="form-control form-control-sm border-0 bg-light">
        </div>

        <div class="row g-3">
          <div class="col-8">
            <label class="form-label text-muted mb-1" style="font-size:.8rem;">Город</label>
            <input type="text" name="address_locality" value="{{ settings_data.address_locality|default:'' }}"
                   class="form-control form-control-sm border-0 bg-light">
          </div>
          <div class="col-4">
            <label class="form-label text-muted mb-1" style="font-size:.8rem;">Индекс</label>
            <input type="text" name="address_postal_code" value="{{ settings_data.address_postal_code|default:'' }}"
                   class="form-control form-control-sm border-0 bg-light">
          </div>
        </div>

      </div>
    </div>

  </div>
</div>
```

</details>

### 2. Email identity (`_email.html`)
Only "who" outgoing emails come from. SMTP transport is configured
exclusively via environment variables (`EMAIL_HOST`, `EMAIL_PORT`,
`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`/`EMAIL_USE_SSL`)
in `settings.py` — not through the cabinet. Form fields map to the
`SiteEmailIdentityMixin` fields: `email_from`, `email_sender_name`,
`email_reply_to`.

> Starting with **codex-django 0.5.1** transport fields (`smtp_host`,
> `smtp_port`, `smtp_user`, `smtp_password`, `smtp_use_tls`,
> `smtp_use_ssl`, `sendgrid_api_key`) have been removed from the library.
> To migrate, move credentials to `EMAIL_*` in your project's `.env` and
> run `makemigrations` + `migrate`.

### 3. Geoposition (`_geo.html`)
Coordinates and map link.

<details>
<summary>Show template code</summary>

```html
{% load i18n %}
<div class="row g-4">
  <div class="col-12">

    <div class="card border-0 shadow-sm mb-3">
      <div class="card-header bg-white border-0 pt-3 pb-0">
        <h6 class="fw-semibold mb-0">Location</h6>
      </div>
      <div class="card-body d-flex flex-column gap-3">

        <div>
          <label class="form-label text-muted mb-1" style="font-size:.8rem;">Google Maps Link</label>
          <input type="text" name="geo_google_maps_link" value="{{ settings_data.geo_google_maps_link|default:'' }}"
                 class="form-control form-control-sm border-0 bg-light" placeholder="https://maps.google.com/?q=...">
        </div>
        <hr class="my-0">

        <div class="row g-3">
          <div class="col-6">
            <label class="form-label text-muted mb-1" style="font-size:.8rem;">Latitude</label>
            <input type="number" step="any" name="geo_lat" value="{{ settings_data.geo_lat|default:'' }}"
                   class="form-control form-control-sm border-0 bg-light" placeholder="55.7558">
          </div>
          <div class="col-6">
            <label class="form-label text-muted mb-1" style="font-size:.8rem;">Longitude</label>
            <input type="number" step="any" name="geo_lon" value="{{ settings_data.geo_lon|default:'' }}"
                   class="form-control form-control-sm border-0 bg-light" placeholder="37.6173">
          </div>
        </div>

      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body p-0 overflow-hidden" style="border-radius: .5rem;">
        <div class="d-flex align-items-center justify-content-center bg-light"
             style="height: 200px; border-radius: .5rem;">
          <div class="text-center text-muted">
            <span class="bi bi-map fs-1 d-block mb-2" style="opacity:.3;"></span>
            <span style="font-size:.85rem;">Map Preview</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>
```

</details>

### 4. Social Networks (`_social.html`)
Links to Telegram, YouTube, and Instagram.

<details>
<summary>Show template code</summary>

```html
{% load i18n %}
<div class="row g-4">
  <div class="col-12">

    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-0 pt-3 pb-0">
        <h6 class="fw-semibold mb-0">Social Media Links</h6>
      </div>
      <div class="card-body">

        <div class="d-flex flex-column gap-0">



          <div class="py-2">
            <label class="form-label text-muted mb-1 d-flex align-items-center gap-2" style="font-size:.8rem;">
              <span class="bi bi-telegram" style="color:#229ed9;"></span> Telegram
            </label>
            <input type="url" name="telegram_url" value="{{ settings_data.telegram_url|default:'' }}"
                   class="form-control form-control-sm border-0 bg-light" placeholder="https://t.me/...">
          </div>
          <hr class="my-0">

          <div class="py-2">
            <label class="form-label text-muted mb-1 d-flex align-items-center gap-2" style="font-size:.8rem;">
              <span class="bi bi-youtube" style="color:#ff0000;"></span> YouTube
            </label>
            <input type="url" name="youtube_url" value="{{ settings_data.youtube_url|default:'' }}"
                   class="form-control form-control-sm border-0 bg-light" placeholder="https://youtube.com/...">
          </div>
          <hr class="my-0">

          <div class="py-2">
            <label class="form-label text-muted mb-1 d-flex align-items-center gap-2" style="font-size:.8rem;">
              <span class="bi bi-instagram" style="color:#e1306c;"></span> Instagram
            </label>
            <input type="url" name="instagram_url" value="{{ settings_data.instagram_url|default:'' }}"
                   class="form-control form-control-sm border-0 bg-light" placeholder="https://instagram.com/...">
          </div>

        </div>

      </div>
    </div>

  </div>
</div>
```

</details>

### 5. Marketing (`_marketing.html`)
Google Analytics, GTM, social media pixels.

<details>
<summary>Show template code</summary>

```html
{% load i18n %}
<div class="row g-4">
  <div class="col-12">

    <div class="card border-0 shadow-sm mb-3">
      <div class="card-header bg-white border-0 pt-3 pb-0">
        <h6 class="fw-semibold mb-0">Analytics and Pixels</h6>
      </div>
      <div class="card-body d-flex flex-column gap-3">

        <div>
          <label class="form-label text-muted mb-1 d-flex align-items-center gap-2" style="font-size:.8rem;">
            Google Analytics ID
          </label>
          <input type="text" name="google_analytics_id" class="form-control form-control-sm border-0 bg-light"
                 value="{{ settings_data.google_analytics_id|default:'' }}" placeholder="G-XXXXXXXXXX">
        </div>
        <hr class="my-0">

        <div>
          <label class="form-label text-muted mb-1 d-flex align-items-center gap-2" style="font-size:.8rem;">
            Google Tag Manager ID
          </label>
          <input type="text" name="google_tag_manager_id" class="form-control form-control-sm border-0 bg-light"
                 value="{{ settings_data.google_tag_manager_id|default:'' }}" placeholder="GTM-XXXXXXX">
        </div>
        <hr class="my-0">

        <div>
          <label class="form-label text-muted mb-1 d-flex align-items-center gap-2" style="font-size:.8rem;">
            Facebook Pixel ID
          </label>
          <input type="text" name="facebook_pixel_id" class="form-control form-control-sm border-0 bg-light"
                 value="{{ settings_data.facebook_pixel_id|default:'' }}" placeholder="000000000000000">
        </div>
        <hr class="my-0">

        <div>
          <label class="form-label text-muted mb-1 d-flex align-items-center gap-2" style="font-size:.8rem;">
            TikTok Pixel ID
          </label>
          <input type="text" name="tiktok_pixel_id" class="form-control form-control-sm border-0 bg-light"
                 value="{{ settings_data.tiktok_pixel_id|default:'' }}" placeholder="CXXXXXXXXXXXXXXXXX">
        </div>

      </div>
    </div>

  </div>
</div>
```

</details>

### 6. Technical Settings (`_technical.html`)
App Mode, Maintenance Mode, head/body script injection.

<details>
<summary>Show template code</summary>

```html
{% load i18n %}
<div class="row g-4">
  <div class="col-12">

    <div class="card border-0 shadow-sm mb-3">
      <div class="card-header bg-white border-0 pt-3 pb-0">
        <h6 class="fw-semibold mb-0">Operation Modes</h6>
      </div>
      <div class="card-body d-flex flex-column gap-0">

        <div class="d-flex align-items-center justify-content-between py-3">
          <div>
            <div style="font-size:.9rem; font-weight:500;">App Mode</div>
            <div class="text-muted" style="font-size:.8rem;">
              Enables PWA functionality and native behavior on mobile devices.
            </div>
          </div>
          <div class="form-check form-switch ms-3 flex-shrink-0">
            <input name="app_mode_enabled" class="form-check-input" type="checkbox" role="switch"
                   {% if settings_data.app_mode_enabled %}checked{% endif %} style="width:2.2em;height:1.2em;">
          </div>
        </div>
        <hr class="my-0">

        <div class="d-flex align-items-center justify-content-between py-3">
          <div>
            <div class="d-flex align-items-center gap-2" style="font-size:.9rem; font-weight:500;">
              Maintenance Mode
            </div>
          </div>
          <div class="form-check form-switch ms-3 flex-shrink-0">
            <input name="maintenance_mode" class="form-check-input" type="checkbox" role="switch"
                   {% if settings_data.maintenance_mode %}checked{% endif %} style="width:2.2em;height:1.2em;">
          </div>
        </div>

      </div>
    </div>

    <div class="card border-0 shadow-sm mb-3">
      <div class="card-header bg-white border-0 pt-3 pb-0">
        <h6 class="fw-semibold mb-0">Custom Scripts</h6>
      </div>
      <div class="card-body d-flex flex-column gap-3">

        <div>
          <label class="form-label text-muted mb-1" style="font-size:.8rem;">Head Scripts</label>
          <textarea name="head_scripts" class="form-control form-control-sm font-monospace border-0 bg-light"
                    rows="4"
                    style="font-size:.8rem; resize:vertical;">{{ settings_data.head_scripts|default:'' }}</textarea>
        </div>
        <hr class="my-0">

        <div>
          <label class="form-label text-muted mb-1" style="font-size:.8rem;">Body Scripts</label>
          <textarea name="body_scripts" class="form-control form-control-sm font-monospace border-0 bg-light"
                    rows="4"
                    style="font-size:.8rem; resize:vertical;">{{ settings_data.body_scripts|default:'' }}</textarea>
        </div>

      </div>
    </div>

  </div>
</div>
```

</details>
