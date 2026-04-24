from __future__ import annotations

from pathlib import Path

import pytest
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.test import RequestFactory, override_settings

from codex_django.showcase.mock import ShowcaseMockData

pytestmark = pytest.mark.unit
REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_SETTINGS = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [REPO_ROOT / "src" / "codex_django" / "showcase" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "codex_django.cabinet.context_processors.cabinet",
                "codex_django.cabinet.context_processors.notifications",
            ],
        },
    }
]


def _request(path: str = "/showcase/"):
    request = RequestFactory().get(path)
    request.user = AnonymousUser()
    return request


@pytest.mark.parametrize(
    ("template", "context", "expected"),
    [
        (
            "showcase/cabinet/dashboard/index.html",
            ShowcaseMockData.get_dashboard_context(),
            ("chartWidget", "donutWidget", "Top Specialists"),
        ),
        (
            "showcase/cabinet/staff/index.html",
            ShowcaseMockData.get_staff_context(),
            ("cab-card-grid", "cab-data-table", "cab-data-table__cards"),
        ),
        (
            "showcase/cabinet/clients/index.html",
            ShowcaseMockData.get_clients_context(),
            ("cab-card-grid", "cab-data-table", "cab-data-table__cards"),
        ),
        (
            "showcase/cabinet/booking/index.html",
            ShowcaseMockData.get_booking_schedule_context(),
            ("cab-calendar", "cab-calendar__event"),
        ),
        (
            "showcase/cabinet/booking/appointments.html",
            ShowcaseMockData.get_booking_appointments_context(),
            ("cab-data-table", "cab-data-table__cards"),
        ),
        (
            "showcase/cabinet/analytics/reports.html",
            ShowcaseMockData.get_reports_context(),
            ("cab-report", "cab-report-table", "chartWidget"),
        ),
        (
            "showcase/cabinet/conversations/index.html",
            ShowcaseMockData.get_conversations_context(),
            ("cab-split-panel", "split-panel-detail"),
        ),
        (
            "showcase/cabinet/notifications/log.html",
            ShowcaseMockData.get_notifications_log_context(),
            ("cab-data-table", "cab-data-table__cards"),
        ),
    ],
)
@override_settings(DEBUG=True, STATIC_URL="/static/", TEMPLATES=TEMPLATE_SETTINGS)
def test_showcase_pages_render_library_components(template: str, context: dict[str, object], expected: tuple[str, ...]):
    html = render_to_string(template, context, request=_request())

    for marker in expected:
        assert marker in html
    assert "showcase/cabinet/css/cabinet.css" not in html
    assert "showcase/cabinet/widgets/" not in html


def test_showcase_templates_do_not_reference_duplicate_cabinet_assets():
    root = REPO_ROOT / "src" / "codex_django" / "showcase"
    haystack = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.html"))

    assert "showcase/cabinet/widgets/" not in haystack
    assert "showcase/cabinet/includes/" not in haystack
    assert "showcase/cabinet/css/" not in haystack
    assert "showcase/cabinet/js/" not in haystack
