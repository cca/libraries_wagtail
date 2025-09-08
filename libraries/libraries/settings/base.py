# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import io
import json
import os

import dj_database_url
from google.cloud import secretmanager
from google.oauth2.service_account import Credentials

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# need a default NS so we can run collectstatic (e.g. in Dockerfile)
env = os.environ.copy()
namespace = env.get("KUBERNETES_NAMESPACE", "libraries-wagtail")
match namespace:
    case "libraries-wagtail":
        environment = "local"
        WAGTAILADMIN_BASE_URL = "http://127.0.0.1"
        DEBUG = True
        CACHES = {
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
if not "DOCKER_BUILD" in env:
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
SECRET_KEY = env.get(
    "SECRET_KEY", r"ud-bm(brnp^zez%(=fv(5n=u1j1vr$_vxsg=lrhadzo%un-%gb"
)
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

# SSO/AUTH
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "django_cas_ng.backends.CASBackend",
]
CAS_CREATE_USER = False
CAS_FORCE_CHANGE_USERNAME_CASE = "lower"
CAS_LOGOUT_COMPLETELY = True
CAS_SERVER_URL = env.get("CAS_SERVER_URL", "")
LOGIN_URL = "cas_ng_login"
WAGTAIL_FRONTEND_LOGIN_URL = LOGIN_URL
WAGTAIL_PASSWORD_RESET_ENABLED = False

# caching in staging & production
if environment != "local":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "libraries_wagtail_cache",
        }
    }
    CACHE_MIDDLEWARE_ALIAS = "default"
    CACHE_MIDDLEWARE_SECONDS = 300
    CACHE_MIDDLEWARE_KEY_PREFIX = "ccalib"

ROOT_URLCONF = "libraries.urls"

LOGIN_REDIRECT_URL = "wagtailadmin_home"

WSGI_APPLICATION = "libraries.wsgi.application"

# Mail
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = env.get("GOOGLE_SMTP_USER", "")
EMAIL_HOST_PASSWORD = env.get("GOOGLE_SMTP_PASS", "")

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Los_Angeles"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Allow AIVF (5.1) & SVG (5.0) uploads
WAGTAILIMAGES_EXTENSIONS: list[str] = [
    "avif",
    "gif",
    "jpg",
    "jpeg",
    "png",
    "svg",
    "webp",
]
# https://docs.wagtail.org/en/stable/advanced_topics/images/image_file_formats.html#image-file-formats
# By default AVIF and WEBP are converted to PNG but we would rather use the more modern formats
WAGTAILIMAGES_FORMAT_CONVERSIONS: dict[str, str] = {
    "avif": "avif",
    "webp": "webp",
}

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
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"
# necessary to serve Summon files or any arbitrary static file
WHITENOISE_ROOT = STATIC_ROOT

# these settings seem to still be necessary but note that we serve media from
# a Google Storage Bucket — see the Google Cloud section at the bottom
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

FILE_UPLOAD_PERMISSIONS = 0o644

####################
# Wagtail settings #
####################

WAGTAIL_SITE_NAME = "CCA Libraries & Instructional Technology"
# https://docs.wagtail.org/en/latest/reference/settings.html#wagtaildocs-serve-method
# We've used this in the past to ensure document requests are logged and aren't
# forced downloads but it's no longer needed & we have no persistent logs.
# WAGTAILDOCS_SERVE_METHOD = 'redirect'

# https://docs.wagtail.org/en/stable/reference/settings.html#wagtailadmin-unsafe-page-deletion-limit
WAGTAILADMIN_UNSAFE_PAGE_DELETION_LIMIT = 5

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

# https://docs.wagtail.org/en/latest/reference/settings.html#wagtailadmin-external-link-conversion
WAGTAIL_EXTERNAL_LINK_CONVERSION = "confirm"

ADMINS = (("Eric Phetteplace", "ephetteplace@cca.edu"),)
# don't send these emails, they tend to be redundant with ones moderators get anyways
WAGTAILADMIN_NOTIFICATION_INCLUDE_SUPERUSERS = False

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
if "DATABASE_URL" in env:
    DATABASES = {"default": dj_database_url.config()}

# Brokenlinks app - "Summon Broken Links for Website Tests" Google Form
# These are the input name attribute values if
# They're the same for test & live forms, maybe because test is a copy?
BROKENLINKS_HASH: dict[str, str] = {
    "openurl": "entry.1430108689",
    "permalink": "entry.743539962",
    "type": "entry.1515176237",
    "email": "entry.1509607699",
    "comments": "entry.249064033",
}
if environment == "production":
    BROKENLINKS_GOOGLE_SHEET_URL = "https://docs.google.com/forms/d/e/1FAIpQLSehVHSXLkZ5_gcAYxh5ZEktbU-0axbakVONq9lavfP1SXGc_A/formResponse"
else:
    # test form for local and staging
    BROKENLINKS_GOOGLE_SHEET_URL = "https://docs.google.com/forms/d/16CqNzTnkLot289CqWcUVZf99KdxFaGp2Patu0Vri2Ok/formResponse"

# Summon app
SUMMON_SFTP_UN = "cdi_cca-catalog@customers.na"
SUMMON_SFTP_HOST = "cdi-providers-dc01.hosted.exlibrisgroup.com"
SUMMON_REPORT_URL = (
    "https://library.cca.edu/cgi-bin/koha/svc/report?id=152&sql_params={}"
)

# Search Backend
ES_INDEX_SETTINGS = {
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
WAGTAILSEARCH_BACKENDS = {
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

# Template caching
TEMPLATES = [
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

# ------------ #
# Google Cloud #
# ------------ #
if not "DOCKER_BUILD" in env:
    INSTALLED_APPS += ("storages",)
    STORAGES["default"] = {"BACKEND": "storages.backends.gcloud.GoogleCloudStorage"}
    GS_BUCKET_NAME = env.get("GS_BUCKET_NAME", "")
    GS_OBJECT_PARAMETERS = {"cache_control": "public, max-age=31536000"}
    # Ensure uploaded files are given distinct names, as per valid Django storage behaviour
    GS_FILE_OVERWRITE = False
