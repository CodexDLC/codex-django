"""
Test settings — used only for pytest.

Inherits from base settings but uses SQLite in-memory for speed.
"""

from .base import *  # noqa: F403

# Enable debug mode in tests for detailed error pages
DEBUG = True

# SQLite in-memory database for fast tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# In-memory cache for tests (no Redis)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

# Disable Redis password for tests
REDIS_PASSWORD = None

# Email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable migrations for speed (optional)
# MIGRATION_MODULES = {app: None for app in INSTALLED_APPS}

# Fast password hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
