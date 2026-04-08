# Settings

Our current setup only use a `base.py` settings file with a few conditional expressions based on the k8s namespace environment variable to `DEBUG` and the site's `WAGTAILADMIN_BASE_URL`. This base and its conditions handle our local development, staging, and production environnments. Env-specific settings are mostly loaded through Google Secret Manager.

There is also a `test.py` settings file which is solely used during tests. It ensures tests can be run without external services (GCP CDN, Elasticsearch, Postgres).

## Specifying which settings to use

Running `python manage.py runserver --settings libraries.settings.base` loads a specific settings module with the testing server. The Skaffold dev server executes the `runserver` command without specifying a settings module (see kubernetes/local/scripts/init.sh) which defaults to loading `libraries.settings.base`.

Using uWSGI, add a line like `env = DJANGO_SETTINGS_MODULE=libraries.settings.base` to the uwsigi.ini file (see kubernetes/uwsgi.ini) being referenced by uwgsi's startup command (see Dockerfile).
