"""
Settings shared between base and test settings files.
"""
# INSTALLED_APPS and MIDDLEWARE cannot be shared because we want to disable
# things like whitenoise, CAS, and caching during tests.

# sets of HTML tags allowed in various rich text fields
# full list here:
# https://docs.wagtail.io/en/latest/advanced_topics/customisation/page_editing_interface.html#rich-text-features
import os
from typing import Any

PROJECT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR: str = os.path.dirname(PROJECT_DIR)

RICHTEXT_BASIC: list[str] = [
    "bold",
    "document-link",
    "italic",
    "link",
    "strikethrough",
    "subscript",
    "superscript",
]
RICHTEXT_ADVANCED: list[str] = RICHTEXT_BASIC + [
    "code",
    "embed",
    "h3",
    "hr",
    "image",
    "ol",
    "ul",
]
STATIC_URL: str = "/static/"
TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
