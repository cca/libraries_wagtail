# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import io
import json
import os
from typing import Any

import dj_database_url
from google.cloud import secretmanager
from google.oauth2.service_account import Credentials

PROJECT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR: str = os.path.dirname(PROJECT_DIR)

# need a default NS so we can run collectstatic (e.g. in Dockerfile)
env: dict[str, str] = os.environ.copy()
namespace: str = env.get("KUBERNETES_NAMESPACE", "libraries-wagtail")
match namespace:
    case "libraries-wagtail":
        environment: str = "local"
        WAGTAILADMIN_BASE_URL: str = "http://127.0.0.1"
        DEBUG: bool = True
        CACHES: dict[str, dict[str, str]] = {
            "default": {
                "BACKEND": "django.core.cache.backends.dummy.DummyCache",
            }
        }

    case "lib-ep":
        environment = "staging"
        WAGTAILADMIN_BASE_URL = "https://libraries-libep.cca.edu"

    case "lib-production":
        environment = "production"
        WAGTAILADMIN_BASE_URL = "https://libraries.cca.edu"

    case _:
        raise RuntimeError(f"Unknown namespace: {namespace}")

# values we don't want set during a docker build
if "DOCKER_BUILD" not in env:
    # Load GCP credentials from service account key
    GS_CREDENTIALS = Credentials.from_service_account_info(
        json.loads(env.get("GS_CREDENTIALS", ""))
    )
    if environment != "local":
        # read values from Google Secret Manager into environment, used for DB and ES URLs
        smclient = secretmanager.SecretManagerServiceClient(credentials=GS_CREDENTIALS)
        secret = f"projects/{env['GS_PROJECT_ID']}/secrets/libraries_{environment}/versions/latest"
        payload = smclient.access_secret_version(name=secret).payload.data.decode(
            "utf-8"
        )
        for line in io.StringIO(payload):
            key, value = line.strip().split("=", 1)
            env[key] = value

# TODO we'd like to hide this but docker image won't build without it
# TODO because we run a mgmt cmd (collectstatic)
SECRET_KEY: str = env.get(
    "SECRET_KEY", r"ud-bm(brnp^zez%(=fv(5n=u1j1vr$_vxsg=lrhadzo%un-%gb"
)
ALLOWED_HOSTS: list[str] = ["*"]

INSTALLED_APPS: list[str] = [
    # let whitenoise serve static files instead of Django
    "whitenoise.runserver_nostatic",
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
    "django_cas_ng",
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
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_cas_ng.middleware.CASMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]

REST_FRAMEWORK: dict[str, tuple[str]] = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

# SSO/AUTH
AUTHENTICATION_BACKENDS: list[str] = [
    "django.contrib.auth.backends.ModelBackend",
    "django_cas_ng.backends.CASBackend",
]
CAS_CREATE_USER: bool = False
CAS_FORCE_CHANGE_USERNAME_CASE: str = "lower"
CAS_LOGOUT_COMPLETELY: bool = True
CAS_SERVER_URL: str = env.get("CAS_SERVER_URL", "")
LOGIN_URL: str = "cas_ng_login"
WAGTAIL_FRONTEND_LOGIN_URL: str = LOGIN_URL
WAGTAIL_PASSWORD_RESET_ENABLED: bool = False

# caching in staging & production
if environment != "local":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "libraries_wagtail_cache",
        }
    }
    CACHE_MIDDLEWARE_ALIAS: str = "default"
    CACHE_MIDDLEWARE_SECONDS: int = 300
    CACHE_MIDDLEWARE_KEY_PREFIX: str = "ccalib"

ROOT_URLCONF: str = "libraries.urls"

LOGIN_REDIRECT_URL: str = "wagtailadmin_home"

WSGI_APPLICATION: str = "libraries.wsgi.application"

# Mail
EMAIL_BACKEND: str = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS: bool = True
EMAIL_PORT: int = 587
EMAIL_HOST: str = "smtp.gmail.com"
EMAIL_HOST_USER: str = env.get("GOOGLE_SMTP_USER", "")
EMAIL_HOST_PASSWORD: str = env.get("GOOGLE_SMTP_PASS", "")

# Internationalization
LANGUAGE_CODE: str = "en-us"
TIME_ZONE: str = "America/Los_Angeles"
USE_I18N: bool = True
USE_L10N: bool = True
USE_TZ: bool = True

##########################################
# Static files (CSS, JavaScript, Images) #
##########################################

STORAGES: dict[str, dict[str, str]] = {
    # this is overriden to use Whitenoise/Google Cloud everywhere but during docker build
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}
STATICFILES_DIRS: list[str] = [
    os.path.join(PROJECT_DIR, "static"),
]
STATIC_ROOT: str = os.path.join(BASE_DIR, "static")
STATIC_URL: str = "/static/"
# necessary to serve Summon files or any arbitrary static file
WHITENOISE_ROOT: str = STATIC_ROOT

# these settings seem to still be necessary but note that we serve media from
# a Google Storage Bucket — see the Google Cloud section at the bottom
MEDIA_ROOT: str = os.path.join(BASE_DIR, "media")
MEDIA_URL: str = "/media/"

FILE_UPLOAD_PERMISSIONS = 0o644

####################
# Wagtail settings #
####################

WAGTAIL_SITE_NAME: str = "CCA Libraries & Instructional Technology"

# https://docs.wagtail.org/en/latest/reference/settings.html#wagtaildocs-serve-method
# We've used this in the past to ensure document requests are logged and aren't
# forced downloads but it's no longer needed & we have no persistent logs.
# WAGTAILDOCS_SERVE_METHOD = 'redirect'

# https://docs.wagtail.org/en/stable/reference/settings.html#wagtailadmin-unsafe-page-deletion-limit
WAGTAILADMIN_UNSAFE_PAGE_DELETION_LIMIT: int = 5

# sets of HTML tags allowed in various rich text fields
# full list here:
# https://docs.wagtail.io/en/latest/advanced_topics/customisation/page_editing_interface.html#rich-text-features
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

# Allow AIVF (5.1) & SVG (5.0) uploads
WAGTAILIMAGES_EXTENSIONS: list[str] = [
    "avif",
    "gif",
    "jpg",
    "jpeg",
    "png",
    "svg",
    "webp",
    "heic",
]
# https://docs.wagtail.org/en/stable/advanced_topics/images/image_file_formats.html#image-file-formats
# By default AVIF and WEBP are converted to PNG but we would rather use the more modern formats
WAGTAILIMAGES_FORMAT_CONVERSIONS: dict[str, str] = {
    "avif": "avif",
    "webp": "webp",
}

# https://docs.wagtail.org/en/latest/reference/settings.html#wagtailadmin-external-link-conversion
WAGTAIL_EXTERNAL_LINK_CONVERSION: str = "confirm"

ADMINS: tuple[tuple[str, str]] = (("Eric Phetteplace", "ephetteplace@cca.edu"),)
# don't send these emails, they tend to be redundant with ones moderators get anyways
WAGTAILADMIN_NOTIFICATION_INCLUDE_SUPERUSERS: bool = False

DEFAULT_AUTO_FIELD: str = "django.db.models.AutoField"
if "DATABASE_URL" in env:
    DATABASES: dict[str, Any] = {"default": dj_database_url.config()}

###################
# Brokenlinks app #
###################
# These are the input name attribute values, inspect form to find
BROKENLINKS_HASH: dict[str, str] = {
    "openurl": "entry.1430108689",
    "permalink": "entry.743539962",
    "type": "entry.1515176237",
    "email": "entry.1509607699",
    "comments": "entry.249064033",
}
if environment == "production":
    BROKENLINKS_GOOGLE_SHEET_URL: str = "https://docs.google.com/forms/d/e/1FAIpQLSehVHSXLkZ5_gcAYxh5ZEktbU-0axbakVONq9lavfP1SXGc_A/formResponse"
else:
    # test form for local and staging
    BROKENLINKS_GOOGLE_SHEET_URL: str = "https://docs.google.com/forms/d/16CqNzTnkLot289CqWcUVZf99KdxFaGp2Patu0Vri2Ok/formResponse"

# Summon app
SUMMON_SFTP_UN: str = "cdi_cca-catalog@customers.na"
SUMMON_SFTP_HOST: str = "cdi-providers-dc01.hosted.exlibrisgroup.com"
SUMMON_REPORT_URL: str = (
    "https://library.cca.edu/cgi-bin/koha/svc/report?id=152&sql_params={}"
)

##################
# Search Backend #
##################
ES_INDEX_SETTINGS: dict[str, dict[str, Any]] = {
    "settings": {
        "index": {
            "number_of_shards": "5",
            "number_of_replicas": "1",
        },
        "analysis": {
            "filter": {
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_keywords": {
                    "type": "keyword_marker",
                    "keywords": ["koha", "openequella", "equella", "moodle", "panopto"],
                },
                "english_stemmer": {"type": "stemmer", "language": "english"},
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english",
                },
            },
            "char_filter": {
                "special_char_replace": {
                    "type": "pattern_replace",
                    "pattern": r"[^\p{L}\s]",
                    "replacement": "",
                }
            },
            "analyzer": {
                "english": {
                    "tokenizer": "standard",
                    "filter": [
                        "english_possessive_stemmer",
                        "lowercase",
                        "english_stop",
                        "english_keywords",
                        "english_stemmer",
                    ],
                    "char_filter": ["html_strip"],
                },
                "english_exact": {
                    "tokenizer": "standard",
                    "filter": ["lowercase"],
                    "char_filter": ["html_strip"],
                },
                "alpha_only": {
                    "tokenizer": "standard",
                    "filter": ["lowercase"],
                    "char_filter": ["special_char_replace"],
                    "type": "custom",
                },
            },
        },
    }
}
WAGTAILSEARCH_BACKENDS: dict[str, dict[str, Any]] = {
    "default": {
        "BACKEND": "wagtail.search.backends.elasticsearch7",
        "URLS": [env.get("ES_URL", "")],
        "INDEX": env.get("ES_INDEX_PREFIX", ""),
        "TIMEOUT": 10,
        "OPTIONS": {},
        "AUTO_UPDATE": True,
        "ATOMIC_REBUILD": True,
        "INDEX_SETTINGS": ES_INDEX_SETTINGS,
    }
}

####################
# Template caching #
####################
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
if environment != "local":
    TEMPLATES[0]["APP_DIRS"] = False
    TEMPLATES[0]["OPTIONS"]["loaders"] = [
        (
            "django.template.loaders.cached.Loader",
            [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        ),
    ]

################
# Google Cloud #
################
if "DOCKER_BUILD" not in env:
    INSTALLED_APPS += ("storages",)
    STORAGES["default"] = {"BACKEND": "storages.backends.gcloud.GoogleCloudStorage"}
    GS_BUCKET_NAME = env.get("GS_BUCKET_NAME", "")
    GS_OBJECT_PARAMETERS = {"cache_control": "public, max-age=31536000"}
    # Ensure uploaded files are given distinct names, as per valid Django storage behaviour
    GS_FILE_OVERWRITE = False
