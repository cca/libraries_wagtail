# Starting a Wagtail site

Here's the basic steps to starting this project. We'll assume you're in the root of the project (e.g. the parent of this "docs" directory). You'll need python, virtualenv, postgres, and node (or nvm) installed. See [the Wagtail "getting started" doc](http://docs.wagtail.io/en/v1.10.1/getting_started/tutorial.html) for more.

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

There's a "bootstrap.sh" script that does all this but I list the steps above for precision's sake.

## Settings, Database, & Search

The database and search settings vary the most across local/dev/production environments. We define them in the libraries/libraries/settings/local.py file. I've included an example local.py in the "docs" folder with all the confidential items changed, it can be a useful guide when configuring the site.

We should use a postgres database rather than a sqlite3 one because it's closer to what the production site uses. Here are examples of local postgres and sqlite databases:

```python
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'https://localhost'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'libraries_cca_edu',
        'USER': 'libuser',
        'PASSWORD': 'password', # can be left blank for no password
        'HOST': 'localhost',
    },
    'local': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

The site comes with settings for Elasticsearch but doesn't enable it by default. To enable it, install Elasticsearch, start the ES server, and add a passage like this to libraries/libraries/settings/local.py:

```python
from .elasticsearch import *
# You'll want to override these properties as they vary by installation
WAGTAILSEARCH_BACKENDS['default']['URLS'][0] = 'http://localhost:9200'
WAGTAILSEARCH_BACKENDS['default']['INDEX'] = 'libraries_wagtail_dev'
```

Run `python libraries/manage.py update_index` to create the initial search index.

## Misc Notes

Starting a fresh database with `manage.py migrate` and seeing an error? It's possible that an upgrade to core software (e.g. Wagtail, Django) introduced a new field but prior migrations didn't know about it so errors are thrown. See commit 97970f3 for instance where `django.db.utils.OperationalError: no such column: wagtailcore_page.last_published_at` errors were being thrown until a Wagtailcore migration was added as a dependency before creating the BlogIndex. The solution is to identify the migration in a dependency and add it to our custom migrations.

Want to recreate the production or development database? The basic steps are:

```sh
> # download the media files
> scp -r {{production_server}}:{{wagtail_root}}/libraries/media {{local_root}}/libraries
> # download the db
> ssh {{production_server}} 'pg_dump -h db_host -U db_user db_name > dump.sql'
> scp {{production_server}}:dump.sql .
> # delete any existing postgres db, create a new empty one, execute the dumped SQL
> dropdb libraries_cca_edu
> createdb libraries_cca_edu --owner libuser
> psql libraries_cca_edu < dump.sql
```

It might be a little less straightforward than that but it's close.

## Cron jobs

Wagtail automatically updates the search index and publishes scheduled pages. As we include more management commands, we may require more cron jobs but for now this is the only one that needs to be configured:

```sh
# download latest Instagram post (at least daily, scheduling not hugely important)
* 4 * * * workon libraries; /opt/virtualenvs/libraries/bin/python /opt/libraries_wagtail/libraries/manage.py instagram
```
