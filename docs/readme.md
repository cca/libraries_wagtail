# Libraries Wagtail Site

This folder contains the generic documentation for the CCA Libraries Wagtail site as well as development scripts, all of which are meant to be run from the parent directory. Most of the site's apps also have readme files with more information specific to them.

## Development

Outline:

- Pick an app or feature to work on & checkout a logically-named branch based on the `dev` branch
  - `iss##` for work related to an issue is a fine naming convention
- Start up the local development environment, `./docs/dev.fish up`
- If model or database changes happen, run `makemigrations -n short_name`
  - Try to _always_ name migrations so it's possible infer what it's doing from the filename
  - If you make multiple migrations for the same feature/issue, combine them _before pushing to the remote repo_ with `squashmigrations app_name first_number last_number`
  - It is recommended to indicate that a commit requires running migrations, e.g. by appending `(MIGRATE)` to the end of the first line of the commit message
- Feel free to `git push origin $BRANCH` to save intermediary changes to the remote repo
- Once a feature is complete, checkout `dev` & `git merge $BRANCH` into it
- Push the dev branch to a staging instance `git push && git tag lib-ep-$NUM && git push --tags` then test it at libraries-libep.cca.edu
- Merge tested code into the main branch, `git checkout main` & `git merge dev`
- Write release notes in the CHANGELOG.md and check if any of this documentation needs to be updated
- Push changes to production, `git tag release-$NUM && git push && git push --tags`

See deployment.md for more details on deploying to remote instances like staging and production.

## Tools

**setup.sh** bootstraps the local development environment so we can begin working on the site without needing to push to a remote instance like staging.

**sync.fish** copies a remote instance's data to your local development environment. `./docs/sync.fish --media` does the media files while `./docs/sync.fish --db` does the database. By default it syncs from staging but you can sync from `--prod` as well. Run `./docs/sync.fish --help` for complete usage information.

**dev.fish** starts or stop the local development toolchain (which is: docker, minikube, skaffold). Run `./dev.fish up` or `start` to begin and `./dev.fish down` or `stop` when you're done. Note that this is just a convenience; there's no reason you cannot manage the development tools individually if you want to.

## Sitemap

There are a few layers to the CCA Libraries site. The outline below shows the basic structure with a few annotations:

- The parentheses next to a page's title contain the name of its model
- An asterisk \* denotes a _singleton_ page (e.g. the home page, various indices)
- A caret ^ denotes non-page content (doesn't appear in search results, shouldn't be visited directly in a web browser)

```
Root (Wagtail abstraction)
    |---Home* (home.HomePage)
        |---Services* (categories.CategoryPage)
            |---Instructional Services & Technology^ (categories.RowComponent)
                |---Child content pages...
            |---Circulation Services^ (categories.RowComponent)
                |---Child content pages...
            |---Emerging Projects^ (categories.RowComponent)
                |---Child content pages...
        |---Collections* (categories.CategoryPage)
            |---Collections^ (categories.RowComponent)
                |---Various special collections (categories.SpecialCollectionsPage)
                |---Child content pages...
        |---About Us* (categories.CategoryPage)
            |---About Us^ (categories.RowComponent)
                |---Staff listing* (staff.StaffListPage)
                |---Hours* (hours.HoursPage)
                |---Child content pages...
        |---Blog*^ (blog.BlogIndex)
            |---All blog posts... (blog.BlogPage)
        |---Exhibits* (exhibitions.ExhibitsIndexPage)
            |---All digital exhibitions... (exhibitions.ExhibitPage)
        |---Search (no model, only a view in search/views.py)
        |---Brokenlinks^ (no model, only a view in brokenlinks/views.py)
        |---Instagram^ (instagram.Instagram, used on home page)
        |---Serials Solution API^ (no model, only a view in sersol_api/views.py)
```

The grandchild pages of each main category (Services, Collections, and About Us), represented above with the phrase "child content pages...", can use one of three page models: ServicePage, AboutUsPage, and SpecialCollectionsPage. Each of these pages can then, in turn, have children of any of those three types.

## Static Files

We put _all_ static (CSS, JS) files under the main app's static folder, in libraries/libraries/static. I am not sure if this is a great strategy as it separates apps from their styles (e.g. libraries/exhibitions from libraries/libraries/static/scss/exhibits.scss). Static files are served with the [whitenoise](http://whitenoise.evans.io/en/stable/) middleware add-on.

We use [Gulp](http://gulpjs.com/) for our front-end build tool. Note that tools like autoprefixer are solving some bugs, so switching might result in some style problems (e.g., the radio buttons on the home page search box need autoprefixer).

`npm run` builds the site's assets and `npm watch` watches for changes and rebuilds. See the Gulpfile for more information on these tasks. You should be able to run these tasks on your host laptop and not inside the development app container; the changes will not trigger an image rebuild (which would slow down development terribly) and should be automatically [synced](https://skaffold.dev/docs/pipeline-stages/filesync/) to the container if Skaffold is working properly. Portal takes a different approach to the problem of syncing assets without rebuilding the image and mounts the local application code into the app container as a volume, but this introduces some complexity into the local kubernetes configuration.

There are two folders under the main static directory ("moodle" and "summmon") for hosting static files used in external services that cannot host their own content. The Summon files are contained within this project (see libraries/summon and the summon Gulp tasks) while the Moodle files are created in the [Moodle Styles](https://github.com/cca/moodle-styles) project.

## Miscellaneous Extras

### Migration Tricks

Remember to **always** [squash](https://docs.djangoproject.com/en/4.0/topics/migrations/#squashing-migrations) and name migrations as noted under the development heading.

Sometimes when we create a model, we want to immediately create an instance of it rather than require the admin to create one manually. This lets us create objects like the site's singular home page or top-level categories programmatically, greatly decreasing the time to bootstrap a new iteration of the site. Here are a few examples of this tactic:

- home/migrations/0002_create_homepage.py
- blog/migrations/0003_create_blogindex.py
- categories/migrations/0006_create_categories.py

Note:

- if we generate child pages, we must make sure the migration lists the migration generating the parent page as a dependency (see how create_categories depends upon create_homepage)
- we can disallow certain page types from being created manually at all if we a) generate them during migrations & b) ensure no other model lists them in its `subpage_types`
- `slug`s must be unique & therefore make a good hook when writing the `remove_xxx` method which undoes the effects of the migration

### Wagtail 2.0 / Django 2.0 update

We will likely not need to revisit this but several things changed and the upgrade process wasn't _quite_ straightforward so it's worth documenting a few things. Here was my basic process after updating the Wagtail dependency:

```sh
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
