"""Django app config for optional messaging package templates."""

from __future__ import annotations

from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "codex_django.messaging"
    label = "codex_django_messaging"
    verbose_name = "Codex Django Messaging"
