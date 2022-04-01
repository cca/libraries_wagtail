# Starting a Wagtail site

Here's the basic steps to starting this project. We'll assume you're in the root of the project (e.g. the parent of this "docs" directory). You'll need python, pipenv, postgres, and node (or nvm) installed. See [the Wagtail "getting started" doc](http://docs.wagtail.io/en/v1.10.1/getting_started/tutorial.html) for more.

```sh
> # create virtualenv & install dependencies, enter virtualenv
> pipenv install && pipenv shell
> # install npm dependencies and build front-end assets
> npm install && npm run build
> # create the site database & an admin user
> python libraries/manage.py migrate
> python libraries/manage.py createsuperuser
> # create the cache table—only relevant for production
> python libraries/manage.py createcachetable libraries_wagtail_cache
> # create an initial search index
> python libraries/manage.py update_index
```

Finally, to get animated GIF support from Wand you need to install the imagemagick library [as described in its documentation](http://docs.wand-py.org/en/latest/guide/install.html). I've found that this works fine locally on my Macbook but causes severe problems on our server as large amounts of memory are taken up to generate GIF derivatives.

There's a "bootstrap.sh" script that does all this but I list the steps above for precision's sake.

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

Wagtail automatically updates the search index and publishes scheduled pages. As we include more management commands, we may require more cron jobs.

```sh
# download latest Instagram post (at least daily, scheduling not hugely important)
0 4 * * * workon libraries; /opt/virtualenvs/libraries/bin/python /opt/libraries_wagtail/libraries/manage.py instagram
# send a list of deleted bib records to Summon weekly
0 2 * * 1 workon libraries; /opt/virtualenvs/libraries/bin/python /opt/libraries_wagtail/libraries/manage.py summon_deletes
```
