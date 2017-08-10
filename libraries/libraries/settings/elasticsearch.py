# import this into local settings to enable elasticsearch
# note that you need to install elasticsearch & `pip install elasticsearch` first
# also the URL will change if the ES server is remote
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.wagtailsearch.backends.elasticsearch5',
        'URLS': ['http://localhost:9200'],
        'INDEX': 'libraries_wagtail',
        'TIMEOUT': 5,
        'OPTIONS': {},
        'INDEX_SETTINGS': {},
    }
}
