# Settings

We use a `base.py` settings file with a few conditional expressions based on the k8s namespace env var to set `DEBUG` and the site's `WAGTAILADMIN_BASE_URL`. This base and its conditions handle our local development, staging, and production environnments. Env-specific settings are mostly loaded through Google Secret Manager.

There is also a `test.py` settings file which is solely used during tests. It ensures tests can be run without external services (GCP CDN, Elasticsearch, Postgres) and uses temporary directories for media files to avoid polluting the project directory.

## Test Settings

The test settings file (`test.py`) includes special configurations for running tests:

- **In-memory SQLite database** - Isolated database for each test run
- **Database search backend** - Replaces Elasticsearch with Django's database search
- **Temporary media storage** - Uses Python's `tempfile.gettempdir()` to store uploaded files (like test images) in the system's temporary directory instead of the project root. This prevents test artifacts from cluttering the project and they're automatically cleaned up by the OS.

## Specifying settings to use

Running `python manage.py runserver --settings libraries.settings.base` loads a specific settings module with the testing server. The Skaffold dev server executes the `runserver` command with `libraries.settings.base`.

Using uWSGI, add a line like `env = DJANGO_SETTINGS_MODULE=libraries.settings.base` to the uwsigi.ini file (see kubernetes/uwsgi.ini) being referenced by uwgsi's startup command (see Dockerfile).
