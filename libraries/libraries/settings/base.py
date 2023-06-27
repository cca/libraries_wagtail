# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from __future__ import absolute_import, unicode_literals
import os
import json
import dj_database_url
from google.oauth2.service_account import Credentials

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)
env = os.environ.copy()

namespace = env.get('KUBERNETES_NAMESPACE', None) or env.get('LOCAL_NAMESPACE', None)
if namespace in ['lib-ep', 'lib-mg']:
    DEBUG = True
    # Base URL to use when referring to full URLs within the Wagtail admin backend -
    # e.g. in notification emails. Don't include '/admin' or a trailing slash
    # lib-ep namespace URL is libraries-libep.cca.edu, etc.
    BASE_URL = 'https://libraries-{}.cca.edu'.format(namespace.replace('-',''))
elif namespace == 'lib-production':
    BASE_URL = 'https://libraries.cca.edu'
elif namespace == 'libraries-wagtail': # local namespace
    DEBUG = True
    BASE_URL = 'http://localhost'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # let whitenoise serve static files instead of Django
    'whitenoise.runserver_nostatic',

    # our apps
    'alerts',
    'blog',
    'brokenlinks',
    'categories',
    'exhibitions',
    'home',
    'hours',
    'instagram',
    'search',
    'sersol_api',
    'staff',
    'summon',

    'wagtail.api.v2',
    'wagtail.contrib.forms',
    'wagtail.admin',
    'wagtail.contrib.redirects',
    'wagtail.contrib.styleguide',
    # https://docs.wagtail.org/en/stable/reference/contrib/legacy_richtext.html
    'wagtail.contrib.legacy.richtext',
    # https://docs.wagtail.org/en/stable/reference/contrib/searchpromotions.html
    'wagtail.contrib.search_promotions',
    'wagtail.core',
    'wagtail.documents',
    'wagtail.embeds',
    'wagtail.images',
    'wagtail.search',
    'wagtail.sites',
    'wagtail.snippets',
    'wagtail.users',

    'django_cas_ng',
    'django_extensions',
    'modelcluster',
    'rest_framework',
    'taggit',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
]

# whitenoise must go first
# the 2 cache middleware should sandwich everything else
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',

    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_cas_ng.middleware.CASMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'wagtail.contrib.redirects.middleware.RedirectMiddleware',

    'django.middleware.cache.FetchFromCacheMiddleware',
]

# CAS Authentication github.com/cca/libraries_wagtail/issues/76
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
# SSO/AUTH
CAS_CREATE_USER = False
CAS_FORCE_CHANGE_USERNAME_CASE = 'lower'
CAS_LOGOUT_COMPLETELY = True
CAS_SERVER_URL = env.get('CAS_SERVER_URL', '').rstrip('\n')
LOGIN_URL = 'cas_ng_login'
WAGTAIL_FRONTEND_LOGIN_URL = LOGIN_URL
WAGTAIL_PASSWORD_RESET_ENABLED = False

# caching only in staging, production, not local dev
# https://docs.djangoproject.com/en/3.2/topics/cache/
if namespace == 'libraries-wagtail':
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'libraries_wagtail_cache',
        }
    }
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = 300
    CACHE_MIDDLEWARE_KEY_PREFIX = 'ccalib'

ROOT_URLCONF = 'libraries.urls'

LOGIN_REDIRECT_URL = 'wagtailadmin_home'

from .logging import LOGGING

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'libraries.wsgi.application'

# Mail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = env.get('GOOGLE_SMTP_USER', '').rstrip('\n')
EMAIL_HOST_PASSWORD = env.get('GOOGLE_SMTP_PASS', '').rstrip('\n')

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# necessary to serve Summon files or any arbitrary static file
WHITENOISE_ROOT = STATIC_ROOT

# these settings seem to still be necessary but note that we serve media from
# a Google Storage Bucket — see the Google Cloud section at the bottom
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

FILE_UPLOAD_PERMISSIONS = 0o644

# Wagtail settings

WAGTAIL_SITE_NAME = "CCA Libraries & Instructional Technology"
# https://docs.wagtail.io/en/latest/advanced_topics/settings.html#wagtaildocs-serve-method
# This should be serve_view for us so we can ensure requests are always logged
# WAGTAILDOCS_SERVE_METHOD = 'redirect'

# sets of HTML tags allowed in various rich text fields
# full list here:
# docs.wagtail.io/en/v2.5/advanced_topics/customisation/page_editing_interface.html#rich-text-features
RICHTEXT_BASIC = [
    'bold',
    'document-link',
    'italic',
    'link',
    'strikethrough',
    'subscript',
    'superscript',
]
RICHTEXT_ADVANCED = RICHTEXT_BASIC + [
    'code',
    'embed',
    'h3',
    'hr',
    'image',
    'ol',
    'ul',
]

# https://docs.wagtail.org/en/latest/reference/settings.html#wagtailadmin-external-link-conversion
WAGTAIL_EXTERNAL_LINK_CONVERSION = 'confirm'

# SECRET_KEY = env.get('SECRET_KEY', '').rstrip('\n')
SECRET_KEY = 'ud-bm(brnp^zez%(=fv(5n=u1j1vr$_vxsg=lrhadzo%un-%gb'

ADMINS = (
    ("Eric Phetteplace", "ephetteplace@cca.edu"),
)
# don't send these emails, they tend to be redundant with ones
# that moderators get anyways
WAGTAILADMIN_NOTIFICATION_INCLUDE_SUPERUSERS = False

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
DATABASES = {}
if 'DATABASE_URL' in env:
    DATABASES['default'] = dj_database_url.config()
else:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.get('PGDATABASE', 'cca_libraries'),
        # User, host and port can be configured by the PGUSER, PGHOST and
        # PGPORT environment variables (these get picked up by libpq).
    }

# Brokenlinks app - "Summon Broken Links for Website Tests" Google Form
# test form commented out
# BROKENLINKS_GOOGLE_SHEET_URL = "https://docs.google.com/forms/d/16CqNzTnkLot289CqWcUVZf99KdxFaGp2Patu0Vri2Ok/formResponse"
BROKENLINKS_GOOGLE_SHEET_URL = "https://docs.google.com/forms/d/e/1FAIpQLSehVHSXLkZ5_gcAYxh5ZEktbU-0axbakVONq9lavfP1SXGc_A/formResponse"
BROKENLINKS_HASH = {
    "openurl": "entry.1430108689",
    "permalink": "entry.743539962",
    "type": "entry.1515176237",
    "email": "entry.1509607699",
    "comments": "entry.249064033",
}

# Instagram app
INSTAGRAM_REDIRECT_URI = 'https://libraries.cca.edu/'
INSTAGRAM_APP_ID = env.get('INSTAGRAM_APP_ID', '').rstrip('\n')
INSTAGRAM_APP_SECRET = env.get('INSTAGRAM_SECRET', '').rstrip('\n')

# Summon app
SUMMON_SFTP_UN= 'cdi_cca-catalog@customers.na'
SUMMON_SFTP_HOST = 'cdi-providers-dc01.hosted.exlibrisgroup.com'
SUMMON_REPORT_URL = 'https://library.cca.edu/cgi-bin/koha/svc/report?id=152&sql_params={}'

# Search Backend
ES_INDEX_SETTINGS = {
    'settings': {
        'index': {
            'number_of_shards': '5',
            'number_of_replicas': '1',
        },
        'analysis': {
            'filter': {
                'english_stop': {
                    'type': 'stop',
                    'stopwords': '_english_'
                },
                'english_keywords': {
                    'type': 'keyword_marker',
                    'keywords': ['koha', 'openequella', 'equella', 'moodle', 'panopto']
                },
                'english_stemmer': {
                    'type': 'stemmer',
                    'language': 'english'
                },
                'english_possessive_stemmer': {
                    'type': 'stemmer',
                    'language': 'possessive_english'
                }
            },
            'char_filter': {
                'special_char_replace': {
                    'type': 'pattern_replace',
                    'pattern': '[^\p{L}\s]',
                    'replacement': ''
                }
            },
            'analyzer': {
                'english': {
                    'tokenizer': 'standard',
                    'filter': [
                        'english_possessive_stemmer',
                        'lowercase',
                        'english_stop',
                        'english_keywords',
                        'english_stemmer'
                    ],
                    'char_filter': [
                        'html_strip'
                    ],
                },
                'english_exact': {
                    'tokenizer': 'standard',
                    'filter': [
                        'lowercase'
                    ],
                    'char_filter': [
                        'html_strip'
                    ],
                },
                'alpha_only': {
                    'tokenizer': 'standard',
                    'filter': [
                        'lowercase'
                    ],
                    'char_filter': [
                        'special_char_replace'
                    ],
                    'type': 'custom',
                }
            },
        },
    }
}
ES_URL = env.get('ES_URL', '').rstrip('\n')
ES_INDEX_PREFIX = env.get('ES_INDEX_PREFIX', '').rstrip('\n')
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.elasticsearch5',
        'URLS': [ ES_URL ],
        'INDEX': ES_INDEX_PREFIX,
        'TIMEOUT': 10,
        'OPTIONS': {},
        'AUTO_UPDATE': True,
        'ATOMIC_REBUILD': True,
        'INDEX_SETTINGS': ES_INDEX_SETTINGS,
    }
}

# http://docs.wagtail.io/en/v1.13.1/advanced_topics/performance.html#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates')
        ],
        'OPTIONS': {
            # context_processors copied from base.py
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    }
]


# ------------ #
# Google Cloud #
# ------------ #

# Main service account for GCP
if 'GS_CREDENTIALS' in env:
    INSTALLED_APPS += (
        'storages',
    )

    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = env.get('GS_BUCKET_NAME', '')
    GS_USE_DOMAIN_NAMED_BUCKET = env.get('GS_USE_DOMAIN_NAMED_BUCKET', '') == 'true'

    # Even if the bucket has public permisions, we need to set this
    # setting to `'publicRead'` to retrun a public, non-expiring URL.
    GS_DEFAULT_ACL = 'publicRead'
    GS_OBJECT_PARAMETERS = {
        "cache_control": "public, max-age=31536000"
    }

    # Ensure uploaded files are given distinct names, as per valid Django storage behaviour
    GS_FILE_OVERWRITE = False

    # Load credentials from service account key that grants access
    # to the storage
    GS_CREDENTIALS = Credentials.from_service_account_info(json.loads(env['GS_CREDENTIALS']))
