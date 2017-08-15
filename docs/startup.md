# Starting a Wagtail site

Here's the basic steps to starting this project. We'll assume you're in the root of the project (e.g. the parent of this "docs" directory). See [the Wagtail "getting started" doc](http://docs.wagtail.io/en/v1.10.1/getting_started/tutorial.html) for more. There's a "bootstrap.sh" script that does all this.

```sh
> # create a virtual environment using the python3 interpreter
> virtualenv -p python3 .
> # activate the environment—you'll do this every time you want to work on the project
> # use "activate.fish" below for Fish shell
> source bin/activate
> # install Wagtail & other dependencies in the environment's packages
> pip install -r libraries/requirements.txt
> # install npm dependencies (used for front-end build processes)
> npm install
> # build/minify the frontend assets
> npm run build
> # create the site database & an admin user
> python libraries/manage.py migrate
> python libraries/manage.py createsuperuser
> # create the cache table—only relevant for production
> python libraries/manage.py createcachetable libraries_wagtail_cache
```


## Database & Search

The database and search settings vary the most across local/dev/production environments. We define them in the libraries/settings/local_settings.py file (applied before base settings) and libraries/settings/local.py files (applied after base settings, not used right now). Here's an example local_settings.py:

```python
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'https://localhost'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

The site comes with settings for Elasticsearch but doesn't enable it by default. To enable it, install Elasticsearch, start the ES server, and add a passage like this to libraries/settings/local_settings.py:

```python
from .elasticsearch import *
# You'll want to override these properties as they vary by installation
WAGTAILSEARCH_BACKENDS['default']['URLS'][0] = 'http://localhost:9200'
WAGTAILSEARCH_BACKENDS['default']['INDEX'] = 'libraries_wagtail_dev'
```

Run `python libraries/manage.py update_index` to create the initial search index.


## When you're done

```sh
> # if you've added or updated packages, write them into libraries/requirements.txt
> # turn off the virtualenv
> deactivate
```


## Startup on dev server (libraries-dev.cca.edu vm-lib-django-02.cca.edu) do these as root (sudo)

* cd /opt/libraries_wagtail
* `git pull`
* use libraries virtualenv `workon libraries`
* run a migration `./manage.py migrate`
* restart supervisord: `service supervisord stop` then `service supervisord start`
* (optional) restart nginx `service nginx restart`
