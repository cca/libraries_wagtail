# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'libraries.cca.edu',
    '10.16.8.23',
    'libraries-dev.cca.edu',
    '10.16.8.37',
]

INSTALLED_APPS = [
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

    'wagtail.api.v2',
    'wagtail.contrib.forms',
    'wagtail.admin',
    'wagtail.contrib.redirects',
    'wagtail.contrib.styleguide',
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

# the 2 cache middleware should sandwich everything else
MIDDLEWARE = [
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

CAS_CREATE_USER = False
CAS_FORCE_CHANGE_USERNAME_CASE = 'lower'
CAS_LOGOUT_COMPLETELY = True
CAS_SERVER_URL = 'https://sso.cca.edu/cas/login'
LOGIN_URL = 'cas_ng_login'
WAGTAIL_FRONTEND_LOGIN_URL = LOGIN_URL
WAGTAIL_PASSWORD_RESET_ENABLED = False

# db cache for production, dummy for dev
# https://docs.djangoproject.com/en/1.11/topics/cache/
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'libraries_wagtail_cache',
    },
    'dummy': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    }
}

ROOT_URLCONF = 'libraries.urls'

LOGIN_REDIRECT_URL = 'wagtailadmin_home'

# logging
LOGGING_DIR = os.path.join(BASE_DIR, 'logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'quiet_down_elasticsearch': {
            '()': 'libraries.log.QuietDownElasticsearch',
        },
        'is_404_error': {
            '()': 'libraries.log.is404Error',
        },
        'is_not_404_error': {
            '()': 'libraries.log.isNot404Error',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        # CSV file
        'document': {
            'format': '"{asctime}",{message}',
            'datefmt': "%Y-%m-%d %H:%M:%S",
            'style': '{',
        },
        # django.request logging provides additional HTTP info we're interested in
        'http': {
            'format': '[{asctime}] {levelname} {name}:{lineno} {status_code} {message}',
            'datefmt': "%Y-%m-%d %H:%M:%S",
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'standard': {
            'format': '[{asctime}] {levelname} {name}:{lineno} {message}',
            'datefmt': "%Y-%m-%d %H:%M:%S",
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'standard',
        },
        'log_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'all.log'),
            'filters': ['quiet_down_elasticsearch'],
            'maxBytes': 1024 * 1024 * 10,  # 10M
            'backupCount': 14,
            'formatter': 'standard',
        },
        'document_log_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'documents.csv'),
            'maxBytes': 1024 * 1024 * 10,  # 10M
            'backupCount': 14,
            'formatter': 'document',
        },
        'django_request_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'django_error.log'),
            'filters': ['is_not_404_error'],
            'maxBytes': 1024 * 1024 * 10,  # 10M
            'backupCount': 7,
            'formatter': 'http',
        },
        'not_found_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, '404.log'),
            'filters': ['is_404_error'],
            'maxBytes': 1024 * 1024 * 10,  # 10M
            'backupCount': 7,
            'formatter': 'http',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'include_html': False,
            # Django docs are wrong, even if you have a EMAIL_BACKEND setting
            # you _have_ to specify one here to make AdminEmailHandler work
            'email_backend': 'django.core.mail.backends.smtp.EmailBackend',
        },
        'mgmt_cmd_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'mgmt_cmd.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10M
            'backupCount': 7,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['django_request_file', 'not_found_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'document': {
            'handlers': ['document_log_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'mgmt_cmd.script': {
            'handlers': ['mail_admins', 'mgmt_cmd_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console'],
            'propagate': False,
        },
        '': {
            'handlers': ['log_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

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

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

FILE_UPLOAD_PERMISSIONS = 0o644

# Wagtail settings

WAGTAIL_SITE_NAME = "CCA Libraries & Instructional Technology"
# https://docs.wagtail.io/en/latest/advanced_topics/settings.html#wagtaildocs-serve-method
# This should be serve_view for us so we can ensure requests are always logged
WAGTAILDOCS_SERVE_METHOD = 'serve_view'

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
