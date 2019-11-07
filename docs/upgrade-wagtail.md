# How to Upgrade Wagtail

I've found upgrading Wagtail to be a little less straightforward than I thought, probably because of our server configuration more than anything. Here's what I've had to do:

- edit Pipfile to the new version, then run `pipenv update` to install it
- on the production server, `sudo bash; pipenv shell` to enter the virtualenv as root
- `git pull` to get repo updates and `pipenv update` for installation
- at this point, the live version of the site is still running on the old Wagtail code
- collect the new static files `python libraries/manage.py collectstatic`
- perform any needed database migrations `python libraries/manage.py migrate`
- restart the gunicorn server (`service supervisord stop; sleep 2; service supervisord start`)

## npm Updates are not run with sudo

Note that, while we want to be root while pulling from github and running `manage.py` commands generally, `npm` does not like to be run with `sudo`. It causes general chaos amongst the file permissions. For that reason, a local user (not root) owns the node_modules folder and `npm install` commands should be run as that user. If we're pulling a big update into production—one with Python (Wagtail app code or `pip install` commands), JS, CSS, and NPM changes—then our process looks somewhat like this:

- `sudo git pull` to pull in changes as root
- _not as root_, `npm install`
- with `sudo` again, `npm run build`, `workon libraries`, `pip install -r libraries/requirements.txt`, `manage.py migrate`, `manage.py collectstatic`
- restart the gunicorn server (requires `sudo`)

It may seem counterintuitive that we're not supposed to run npm commands as root but are doing so with `npm run build` but remember that that is actually a task related to our static CSS/JS files, not node_modules, and thus will fail without the proper permissions.

## Wagtail 2.0 / Django 2.0 update

We will likely not need to revisit this but several things changed and the upgrade process wasn't _quite_ straightforward so it's worth documenting a few things. Here was my basic process:

```sh
> workon libraries # activate the app's virtualenv
> pip install --upgrade wagtail
> pip freeze > libraries/requirements.txt
> wagtail updatemodulepaths
> python manage.py migrate
> python manage.py collectstatic
```

- update `django.core.urlresolvers` to `django.urls` wherever it occurs
- delete `django.contrib.auth.middleware.SessionAuthenticationMiddleware` from the `MIDDLEWARE` setting if it's present; it was removed in Django 2.0
- if urls.py has the line `url(r'^django-admin/', include(admin.site.urls))` the `include()` method can be removed such that it's simply "admin.site.urls"
- look for uses of `models.ForeignKey` which don't specify the now-required `on_delete` parameter

Useful docs:

- http://docs.wagtail.io/en/v2.0/releases/2.0.html#upgrade-considerations
- https://docs.djangoproject.com/en/2.0/releases/2.0/
