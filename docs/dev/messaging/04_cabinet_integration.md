# Cabinet Integration — Mirroring the Booking Pattern

The user explicitly asked: "посмотри внимательно как сделан букинг с
сеттингом со своим скорее всего если он внутри проекта чуть позже он
тоже в библиотеку уедет и будет также паттернами расширяться как и
сайт-сеттинг". This document captures the booking pattern and shows
how to mirror it for the messaging cabinet.

## The booking pattern (reference, current)

Booking already has a fully working own-settings cabinet. The pieces:

| File | Role |
|------|------|
| `src/lily_backend/features/booking/booking_settings.py:15` | `BookingSettings` concrete model subclassing `AbstractBookingSettings` from `codex_django.booking.mixins`. |
| `src/lily_backend/features/booking/cabinet.py:11-26` | `declare(module="booking", space="staff", settings_url="cabinet:booking_settings", topbar=…, sidebar=[…])`. |
| `src/lily_backend/cabinet/urls/booking.py:21` | `path("booking/settings/", BookingSettingsView.as_view(), name="booking_settings")`. |
| `src/lily_backend/cabinet/views/booking.py:213` | `BookingSettingsView` (TemplateView) + `BookingSettingsForm` (ModelForm). |
| `templates/cabinet/booking/settings.html` | Form rendering, grouped sections. |

The settings page is **hand-rolled** — there is a dedicated view and
template. It is NOT auto-discovered through the `_*.html` site-settings
pattern.

## The messaging mirror

```
src/lily_backend/features/messaging/
├── messaging_settings.py        # EmailSettings(AbstractEmailSettings, EmailSettingsSyncMixin)
├── cabinet.py                   # declare(module="messaging", settings_url=…)
├── models/
│   ├── __init__.py
│   ├── email_settings.py        # (re-export for convenience)
│   ├── system_recipient.py      # NotificationRecipient(AbstractSystemRecipient)
│   ├── email_log.py             # EmailLog(AbstractEmailLog)
│   ├── thread.py                # Conversation(AbstractThread)
│   ├── message.py               # Message(AbstractMessage)
│   ├── reply.py                 # MessageReply(AbstractMessageReply)
│   └── campaign.py              # Campaign(AbstractCampaign), CampaignRecipient(AbstractCampaignRecipient)
├── services/
├── selector/
└── api/

src/lily_backend/cabinet/
├── urls/
│   └── messaging.py             # path("messaging/settings/", …, name="messaging_settings"), plus inbox/compose/etc.
├── views/
│   └── messaging.py             # MessagingSettingsView, ComposeView, InboxView, …
└── services/
    └── messaging.py             # workflow service (was conversations.py)

templates/cabinet/messaging/
├── settings.html
├── inbox.html
├── compose.html
└── …
```

## `declare()` call

```python
# src/lily_backend/features/messaging/cabinet.py
from codex_django.cabinet import SidebarItem, TopbarEntry, declare
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

declare(
    module="messaging",
    space="staff",
    settings_url="cabinet:messaging_settings",
    topbar=TopbarEntry(
        group="services",
        label=str(_("Inbox")),
        icon="bi-envelope",
        url=reverse_lazy("cabinet:messaging_inbox"),
    ),
    sidebar=[
        SidebarItem(label=str(_("Compose")),       url=reverse_lazy("cabinet:messaging_compose"),       icon="bi-pencil-square"),
        SidebarItem(label=str(_("Inbox")),         url=reverse_lazy("cabinet:messaging_inbox"),         icon="bi-inbox"),
        SidebarItem(label=str(_("Imported Mail")), url=reverse_lazy("cabinet:messaging_imported"),      icon="bi-cloud-download"),
        SidebarItem(label=str(_("Processed")),     url=reverse_lazy("cabinet:messaging_processed"),     icon="bi-check2-circle"),
        SidebarItem(label=str(_("All")),           url=reverse_lazy("cabinet:messaging_all"),           icon="bi-archive"),
        SidebarItem(label=str(_("Campaigns")),     url=reverse_lazy("cabinet:messaging_campaigns"),     icon="bi-megaphone"),
        SidebarItem(label=str(_("New Campaign")),  url=reverse_lazy("cabinet:messaging_campaign_new"),  icon="bi-broadcast"),
        SidebarItem(label=str(_("Recipients")),    url=reverse_lazy("cabinet:messaging_recipients"),    icon="bi-people"),
    ],
)
```

The sidebar items are taken directly from the screenshot the user
shared — same labels, same icon vocabulary as the booking module.

`settings_url` resolves to the settings tab in the topbar
configuration screen (the cabinet UI provides a gear icon that links
to whatever URL the module declares).

## `MessagingSettingsView`

Mirrors `BookingSettingsView` (lily today,
`cabinet/views/booking.py:213`):

```python
# src/lily_backend/cabinet/views/messaging.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from features.messaging.messaging_settings import EmailSettings
from .forms.messaging_settings import EmailSettingsForm


class MessagingSettingsView(LoginRequiredMixin, UpdateView):
    model = EmailSettings
    form_class = EmailSettingsForm
    template_name = "cabinet/messaging/settings.html"
    success_url = reverse_lazy("cabinet:messaging_settings")

    def get_object(self, queryset=None):
        return EmailSettings.load()
```

## `EmailSettingsForm` — section grouping

Booking groups its settings into sections via a `SECTION_FIELDS` dict
on the form. Mirror the same approach:

```python
class EmailSettingsForm(forms.ModelForm):
    SECTION_FIELDS = {
        "identity": [
            "email_from",
            "email_sender_name",
            "email_reply_to",
        ],
        "branding": [
            "site_base_url",
            "logo_url",
        ],
        "transactional_paths": [
            "url_path_confirm",
            "url_path_cancel",
            "url_path_reschedule",
            "url_path_contact_form",
        ],
    }

    class Meta:
        model = EmailSettings
        fields = [field for fields in EmailSettingsForm.SECTION_FIELDS.values() for field in fields]

    @property
    def grouped_fields(self):
        return {
            section: [self[field_name] for field_name in field_names]
            for section, field_names in self.SECTION_FIELDS.items()
        }
```

## Cabinet URLs (single file)

```python
# src/lily_backend/cabinet/urls/messaging.py
from django.urls import path
from cabinet.views.messaging import (
    MessagingSettingsView,
    InboxView,
    ComposeView,
    CampaignsListView,
    CampaignNewView,
    RecipientsView,
    # …
)

urlpatterns = [
    path("messaging/",                     InboxView.as_view(),         name="messaging_inbox"),
    path("messaging/settings/",            MessagingSettingsView.as_view(), name="messaging_settings"),
    path("messaging/compose/",             ComposeView.as_view(),       name="messaging_compose"),
    path("messaging/imported/",            ImportedMailView.as_view(),  name="messaging_imported"),
    path("messaging/processed/",           ProcessedView.as_view(),     name="messaging_processed"),
    path("messaging/all/",                 AllMessagesView.as_view(),   name="messaging_all"),
    path("messaging/campaigns/",           CampaignsListView.as_view(), name="messaging_campaigns"),
    path("messaging/campaigns/new/",       CampaignNewView.as_view(),   name="messaging_campaign_new"),
    path("messaging/recipients/",          RecipientsView.as_view(),    name="messaging_recipients"),
]
```

Mounted from `cabinet/urls/__init__.py` at `/cabinet/`.

## Cabinet bridge — `MessagingBridge`

`codex-django` ships a `MessagingBridge` (analogue to
`BookingBridge`) that exposes type-safe state DTOs to cabinet panels:

```python
@dataclass
class InboxPanelState:
    threads: list[ThreadSummary]
    unread_count: int
    filters: dict[str, Any]


class MessagingBridge:
    def get_inbox_state(self, *, user, filters: dict[str, Any]) -> InboxPanelState: ...
    def get_compose_form_state(self, *, user) -> ComposeFormState: ...
    def get_settings_form_state(self) -> EmailSettingsForm: ...
```

Projects subclass this to inject their concrete models. The bridge
gives cabinet templates a stable, testable interface independent of
HTMX wiring.

## Anti-patterns

* **Auto-discovering messaging settings as a `_messaging.html` partial
  inside the site-settings tab.** That is the old approach for global
  branding settings; messaging gets its own page like booking.
* **Using a single `MessagingViewSet` that owns inbox + compose +
  campaigns.** Booking has separate views per concern; messaging
  follows the same shape — easier to test, easier to permission-gate.
* **Putting the cabinet templates inside `codex_django.messaging`.**
  Templates are project-side because every project's cabinet has its
  own visual design.
