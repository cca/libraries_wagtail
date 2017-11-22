from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm(zvr$pcz%5x*4qfpgs7*h#p(j15+cd&j^@ksb_^t2clblu5)^'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'https://libraries-dev.cca.edu'

try:
    from .local import *
except ImportError:
    pass

# (fake) caching for development
CACHE_MIDDLEWARE_ALIAS = 'dummy'
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = ''
