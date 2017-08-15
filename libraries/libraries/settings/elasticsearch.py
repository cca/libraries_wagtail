# import this into local settings to enable elasticsearch
# note that you need to install elasticsearch & `pip install elasticsearch` first
# also the URL will change if the ES server is remote
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.wagtailsearch.backends.elasticsearch5',
        # Override both URLS and INDEX properties in local settings like
        # from .elasticsearch import *
        # WAGTAILSEARCH_BACKENDS['default']['URLS'] = "http://example.com:9200"
        # WAGTAILSEARCH_BACKENDS['default']['INDEX'] = "libraries_wagtail_dev"
        'URLS': ['http://localhost:9200'],
        'INDEX': 'libraries_wagtail',
        'TIMEOUT': 5,
        'OPTIONS': {},
        'INDEX_SETTINGS': {},
    }
}
