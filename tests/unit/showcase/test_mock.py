"""Unit tests for showcase mock notification contexts."""

from __future__ import annotations

import pytest

from codex_django.showcase.mock import ShowcaseMockData


@pytest.mark.unit
def test_notifications_log_context_filters_by_channel_and_status():
    context = ShowcaseMockData.get_notifications_log_context(channel="telegram", status="failed")

    assert context["active_section"] == "notifications"
    assert context["active_channel"] == "telegram"
    assert context["active_status"] == "failed"
    assert context["entries"]
    assert all(entry["channel"] == "telegram" for entry in context["entries"])
    assert all(entry["status"] == "failed" for entry in context["entries"])


@pytest.mark.unit
def test_notifications_log_context_exposes_summary_tabs():
    context = ShowcaseMockData.get_notifications_log_context()

    assert context["stats"]["total"] >= len(context["entries"])
    assert {tab["key"] for tab in context["channel_tabs"]} == {"all", "email", "telegram"}
    assert {tab["key"] for tab in context["status_tabs"]} == {"all", "sent", "failed", "pending"}


@pytest.mark.unit
def test_notification_templates_context_enriches_channel_details():
    context = ShowcaseMockData.get_notification_templates_context()

    assert context["active_section"] == "notifications"
    assert context["templates"]
    assert all(template["channel_details"] for template in context["templates"])
    assert all("label" in channel for template in context["templates"] for channel in template["channel_details"])
