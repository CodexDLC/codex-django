SECRET_KEY = "test-secret-key-not-for-production"  # noqa: S105  # pragma: allowlist secret
DEBUG = True
ALLOWED_HOSTS: list[str] = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "codex_django",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Referenced by codex_django source (all have safe defaults via getattr)
REDIS_URL = "redis://localhost:6379/0"
PROJECT_NAME = "codex-django-test"
