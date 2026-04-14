"""
Test settings for running CMS tests.

Disables external dependencies like Elasticsearch and uses in-memory database.
"""

import tempfile

# ruff: noqa: F401
from libraries.settings.shared import (
    BASE_DIR,
    PROJECT_DIR,
    RICHTEXT_ADVANCED,
    RICHTEXT_BASIC,
    STATIC_URL,
    TEMPLATES,
)

INSTALLED_APPS: list[str] = [
    # our apps
    "alerts",
    "blog",
    "brokenlinks",
    "categories",
    "exhibitions",
    "home",
    "hours",
    "instagram",
    "search",
    "sersol_api",
    "staff",
    "summon",
    "wagtail.api.v2",
    "wagtail.contrib.forms",
    "wagtail.admin",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.styleguide",
    # https://docs.wagtail.org/en/stable/reference/contrib/legacy_richtext.html
    "wagtail.contrib.legacy.richtext",
    # https://docs.wagtail.org/en/stable/reference/contrib/searchpromotions.html
    "wagtail.contrib.search_promotions",
    "wagtail.contrib.table_block",
    "wagtail",
    "wagtail.documents",
    "wagtail.embeds",
    "wagtail.images",
    "wagtail.search",
    "wagtail.sites",
    "wagtail.snippets",
    "wagtail.users",
    "django_extensions",
    "modelcluster",
    "rest_framework",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
]
# security followed by whitenoise are first
# the 2 cache middleware should sandwich everything else
MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

# Use a simple in-memory test database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Use database search backend instead of Elasticsearch
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Use in-memory cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Use simple static files storage for tests (no manifest)
# Override the STORAGES dict to avoid CompressedManifestStaticFilesStorage
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Disable host checking for tests
ALLOWED_HOSTS = ["*"]

# Use temporary directory for media files during tests
# This prevents test images from being saved to the project directory
MEDIA_ROOT = tempfile.gettempdir()
