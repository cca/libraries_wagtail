# Settings

Flow of settings as they're loaded:

base -> dev or production (branch) -> local (machine) -> elasticsearch

base.py — _universal_ settings that are necessary for all builds of the site, regardless of git branch or machine. Includes lots of Django filler, installed apps, middleware, loggers, and text field settings.

dev.py - runs _development_ builds of the site on both the developer's local machine and our development web host libraries-dev.cca.edu. Typically used when you're on the dev branch. Sets the "email backend" to "console", sets `DEBUG = TRUE`, and uses a dummy cache.

production.py - runs _production_ builds of the site on the live web host, though sometimes we may test these settings locally. Typically used when you're on the `main` branch. Uses an SMTP email backend, `DEBUG = FALSE`, and has caching.

local.py - both dev and production above load this file. It is meant for _machine-specific_ settings such as the `BASE_URL`, `SECRET_KEY`, and `DATABASES` plus app-specific settings for Brokenlinks and Instagram.

elasticsearch.py - the "local" settings above load this file, which establishes some consistent search defaults that can then be overridden locally. This should serve as a model for other apps that introduce complex and machine-variable settings; create a file with defaults which is then overridden in local.py as needed.

Running `python manage.py runserver --settings libraries.settings.production` loads them. **You should be able to test production settings locally.** If that's not possible, then it's likely that a setting needs to be moved down from {dev|production}.py to local.py.
