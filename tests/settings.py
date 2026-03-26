SECRET_KEY = "test-secret-key-not-for-production"  # noqa: S105  # pragma: allowlist secret
DEBUG = True
ALLOWED_HOSTS: list[str] = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "codex_django",
    "codex_django.cabinet",
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
            ],
        },
    },
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
