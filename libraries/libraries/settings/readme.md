# Settings

Our current setup only use a base.py settings file (loaded via the __init__.py file in this directory) in all contexts with a few conditional expressions based on the k8s namespace environment variable to `DEBUG` and the site's `BASE_URL`.

## Old Setup

Wagtail lets us override settings based on context and the local machine. The hierarchy of settings would normally be:

base -> context (e.g. dev, staging, or production) -> local (machine)

base.py — _universal_ settings that are necessary for all builds of the site, regardless of git branch or machine. Includes lots of Django filler, installed apps, middleware, loggers, and text field settings.

dev.py - runs _development_ builds of the site on both the developer's local machine and our development web host libraries-dev.cca.edu. Typically used when you're on the dev branch. Sets the "email backend" to "console", sets `DEBUG = TRUE`, and doesn't use caching.

production.py - runs _production_ builds of the site on the live web host, though sometimes we may test these settings locally. Typically used when you're on the `main` branch. Uses an SMTP email backend, `DEBUG = FALSE`, and has caching.

local.py - the context file would load this. It is meant for _machine-specific_ settings such as the `BASE_URL`, `SECRET_KEY`, and `DATABASES` plus app-specific settings for Brokenlinks and Instagram.

## Specifying which settings to use

Running `python manage.py runserver --settings libraries.settings.dev` loads a specific settings module with the testing server. The Skaffold dev server executes the `runserver` command without specifying a settings module (see kubernetes/local/scripts/init.sh) which defaults to loading `libraries.settings`.

Using uWSGI, add a line like `evn = DJANGO_SETTINGS_MODULE=libraries.settings.dev` to the uwsigi.ini file (see kubernetes/uwsgi.ini) being referenced by uwgsi's startup command (see Dockerfile).
