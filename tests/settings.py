from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "test-secret-key-not-for-production"  # noqa: S105  # pragma: allowlist secret
DEBUG = True
ALLOWED_HOSTS: list[str] = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "codex_django",
    "codex_django.cabinet",
    "codex_django.tracking",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
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

# Sitemap settings (required for patch.object in tests)
CANONICAL_DOMAIN = ""
SITEMAP_LOOKUP_NAMESPACES: list[str] = []
ROOT_URLCONF = "tests.urls"

# Required by encrypted_model_fields (django-encrypted-model-fields)
# Valid Fernet key (32 url-safe base64-encoded bytes). Safe dummy for tests only.
FIELD_ENCRYPTION_KEY = "S4o_caEvaU9JoGsRdwW0PzDFkqyb4_kYUr7lrsTSPMs="  # noqa: S105  # pragma: allowlist secret
