# How to Upgrade Wagtail

I've found upgrading Wagtail to be a little less straightforward than I thought, probably because of our server configuration more than anything. Here's what I've had to do:

- `pip install --upgrade wagtail` locally to test the new version
- once ready, `pip freeze > libraries/requirements.txt` and then `git commit`
- on the production server, `sudo bash; workon libraries` to enter the libraries virtualenv as root
- `git pull` to get repo updates and `pip install -r libraries/requirements.txt` to update Wagtail
- at this point, the live version of the site is still running on the old Wagtail code
- restart the gunicorn server (`service supervisord stop; sleep 2; service supervisord start`)
- but the static files for new admin modules aren't available!?!
- wipe out the old static files `rm -rf static`
- collect the new ones `python libraries/manage.py collectstatic`
- insert them into the repo's static dir `rsync -avz static libraries`

All those final steps around static files feel wonky but that's what's worked for me.

## Wagtail 2.0 / Django 2.0 update

We will likely not need to revisit this but several things changed and the upgrade process wasn't _quite_ straightforward so it's worth documenting a few things. Here was my basic process:

```sh
> workon libraries # activate the app's virtualenv
> pip install --upgrade wagtail
> pip freeze > libraries/requirements.txt
> wagtail updatemodulepaths
> python manage.py migrate
> python manage.py collectstatic
> # static files will 404 on the admin side without this, I don't quite understand
> rsync -avz --delete libraries/static/ libraries/libraries/static/
```

- update `django.core.urlresolvers` to `django.urls` wherever it occurs
- delete `django.contrib.auth.middleware.SessionAuthenticationMiddleware` from the `MIDDLEWARE` setting if it's present; it was removed in Django 2.0
- if urls.py has the line `url(r'^django-admin/', include(admin.site.urls))` the `incude()` method can be removed such that it's simply "admin.site.urls"
- look for uses of `models.ForeignKey` which don't specify the now-required `on_delete` parameter

Useful docs:

- http://docs.wagtail.io/en/v2.0/releases/2.0.html#upgrade-considerations
- https://docs.djangoproject.com/en/2.0/releases/2.0/
