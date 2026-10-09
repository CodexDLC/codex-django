"""Delivery behavior at the Django messaging adapter boundary."""

from unittest.mock import MagicMock, patch

import pytest
from django.core import mail
from django.test import override_settings

from codex_django.messaging.adapters.arq_client import DjangoArqClient
from codex_django.messaging.adapters.direct_adapter import DjangoDirectAdapter

pytestmark = pytest.mark.unit


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="fallback@example.com",
)
def test_direct_adapter_delivers_rendered_content_with_fallback_sender() -> None:
    adapter = DjangoDirectAdapter(use_on_commit=False)

    result = adapter.enqueue(
        "send_notification_task",
        {
            "recipient_email": "reader@example.com",
            "subject": "Welcome",
            "text_content": "Plain text",
            "html_content": "<p>Welcome</p>",
        },
    )

    assert result is None
    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert message.from_email == "fallback@example.com"
    assert message.to == ["reader@example.com"]
    assert message.body == "Plain text"
    assert message.alternatives[0].content == "<p>Welcome</p>"


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="fallback@example.com",
)
def test_direct_adapter_renders_template_and_uses_site_identity() -> None:
    renderer = MagicMock()
    renderer.render.return_value = "<p>Rendered</p>"
    cached_settings = MagicMock()
    cached_settings.load_cached.return_value = {
        "email_from": "team@example.com",
        "email_sender_name": "Team",
    }
    with (
        override_settings(CODEX_SITE_SETTINGS_MODEL="site.SiteSettings"),
        patch("django.apps.apps.get_model", return_value=object()),
        patch("codex_django.core.redis.managers.settings.get_site_settings_manager", return_value=cached_settings),
    ):
        DjangoDirectAdapter(renderer=renderer, use_on_commit=False).enqueue(
            "send_notification_task",
            {
                "mode": "template",
                "template_name": "welcome.html",
                "context_data": {"name": "Ada"},
                "text_content": "Hello Ada",
                "recipient_email": "ada@example.com",
                "subject": "Welcome",
            },
        )

    renderer.render.assert_called_once_with("welcome.html", {"name": "Ada"})
    assert mail.outbox[0].from_email == "Team <team@example.com>"
    assert mail.outbox[0].alternatives[0].content == "<p>Rendered</p>"


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="fallback@example.com",
)
def test_direct_adapter_skips_missing_recipient_and_requires_renderer_for_template() -> None:
    adapter = DjangoDirectAdapter(use_on_commit=False)

    assert adapter.enqueue("task", {"subject": "No recipient"}) is None
    assert len(mail.outbox) == 0
    with pytest.raises(ValueError, match="renderer.*required"):
        adapter.enqueue("task", {"mode": "template", "recipient_email": "ada@example.com"})


@override_settings(DEFAULT_FROM_EMAIL="fallback@example.com", CODEX_SITE_SETTINGS_MODEL="site.SiteSettings")
def test_direct_adapter_falls_back_when_site_settings_lookup_fails() -> None:
    with patch("django.apps.apps.get_model", side_effect=LookupError("not installed")):
        assert DjangoDirectAdapter()._resolve_from_email() == "fallback@example.com"


def test_arq_client_builds_settings_from_secure_url() -> None:
    # Synthetic credentials exercise URL parsing without contacting Redis.
    with override_settings(ARQ_REDIS_URL="rediss://worker:secret@queue.example.com:6380/7"):  # pragma: allowlist secret
        settings = DjangoArqClient.build_redis_settings_from_django()

    assert settings.host == "queue.example.com"
    assert settings.port == 6380
    assert settings.database == 7
    assert settings.username == "worker"
    assert settings.password == "secret"  # pragma: allowlist secret
    assert settings.ssl is True


def test_arq_client_uses_individual_redis_settings_without_url() -> None:
    with override_settings(
        ARQ_REDIS_URL=None,
        REDIS_URL=None,
        REDIS_HOST="redis.internal",
        REDIS_PORT="6381",
        REDIS_PASSWORD="password",  # pragma: allowlist secret
        REDIS_DB="4",
    ):
        settings = DjangoArqClient.build_redis_settings_from_django()

    assert settings.host == "redis.internal"
    assert settings.port == 6381
    assert settings.database == 4
    assert settings.password == "password"  # pragma: allowlist secret
