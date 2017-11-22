from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = False

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

try:
    from .local import *
except ImportError:
    pass

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'https://libraries.cca.edu'

# caching for production
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'ccalib'

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
