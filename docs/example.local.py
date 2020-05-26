import os
from .elasticsearch import *

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'http://localhost'

SECRET_KEY = 'OIJASD(J@(J(ASD)))...'

ADMINS = (
    ("Eric Phetteplace", "ephetteplace@cca.edu"),
)

WAGTAILSEARCH_BACKENDS['default']['URLS'][0] = 'http://localhost:9200'
WAGTAILSEARCH_BACKENDS['default']['INDEX'] = 'libraries_wagtail'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'libraries_cca_edu',
        'USER': 'dbuser',
        'PASSWORD': 'OIJASDIOJ@@@)...',
        'HOST': 'localhost',
        },
    'local': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Brokenlinks app - "TEST - Summon Broken Links" Google Form
BROKENLINKS_GOOGLE_SHEET_KEY = 'OIJASDIOJ@@@)...'
BROKENLINKS_HASH = {
    "ipaddress": "entry.13121312",
    "openurl": "entry.13121313",
    "permalink": "entry.13121314",
    "type": "entry.13121315",
    "email": "entry.13121316",
    "comments": "entry.13121317",
}

# Instagram app
INSTAGRAM_APP_ID = '123987123987456'
INSTAGRAM_APP_SECRET = 'OIJASDIOJ@@@)..'
INSTAGRAM_REDIRECT_URI = 'https://libraries.cca.edu'
