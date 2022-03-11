# Development

Basic outline for working on the site:

- Pick an app or feature to work on & checkout a logically-named branch based on the `dev` branch
  - `iss##` for work related to a GitHub issue is a naming convention
- If model or database changes happen, run `makemigrations -n short_name`
  - Try to _always_ name migrations so it's possible infer what it's doing from the filename
  - If you make multiple migrations for the same feature/issue, combine them _before pushing to GitHub_ with `squashmigrations app_name first_number last_number`
  - It is recommended to indicate that a commit requires running migrations, e.g. by appending `(MIGRATE)` to the end of the first line of the commit message
- Feel free to `git push origin $BRANCH` to save intermediary changes to GitHub
- Once a feature is complete, checkout `dev` & `git merge $BRANCH` into it
- Once `dev` has been tested on another instance of the site, `git checkout main` & `git merge dev`
- Check the readme here to see if models or class names need to be updated

Many features are difficult to test without a full database and media files resembling the live site. The included `wagsync.fish` script will:

- pull down all documents and images (including renditions)
- dump the production postgres database & load it into a local one

Note that you'll need to fill the postgres DB password into the script to make it work, or be prepared to insert the correct password when it runs.

## Shell Commands

These should be run from inside the "libraries" directory as it is the root of the Wagtail site.

```sh
> # update database schema—run after any change to a model
> python manage.py makemigrations -n short_name; python manage.py migrate
> # run a local development server
> python manage.py runserver
> # rebuild the site styles and scripts
> npm run build
> # continually watch for SASS changes & recompile to CSS
> npm run watch
```

We use [Gulp](http://gulpjs.com/) for our front-end build tool. Note that tools like autoprefixer are solving some bugs though so switching might result in some style problems (e.g. the radio buttons on the home page search box need autoprefixer).

## Migration Tricks

Sometimes when we create a model, we want to immediately create an instance of it rather than require the admin to create one manually. This lets us create things like the home page or top-level categories programmatically, greatly decreasing the time to bootstrap a new iteration of the site. Here are a few examples of this tactic:

- home/migrations/0002_create_homepage.py
- blog/migrations/0003_create_blogindex.py
- categories/migrations/0006_create_categories.py

**Notes:**

- if we generate child pages, we must make sure the migration lists the migration generating the parent page as a dependency (see how create_categories depends upon create_homepage)
- we can disallow certain page types from being created manually at all if we a) generate them during migrations & b) ensure no other model lists them in its `subpage_types`
- `slug`s must be unique & therefore make a good hook when writing the `remove_xxx` method which undoes the effects of the migration

## Python versions

We have python 3.5.2 on our server right now, which means we cannot update to Django 3.0 (requires more recent version). Unfortunately, I've been unable to install 3.5.2 on my mac development laptop, I believe due to [pyenv/pyenv#1325](https://github.com/pyenv/pyenv/issues/1325) (a problem with using an older version of openssl via homebrew). I tried uninstalling openssl@1.1.1 and using direct references to the 1.0.1 version in the build flags, nothing worked. So I am testing on 3.5.3 even though we are a minor version behind on the server. Hopefully, when we move to GCP, this problem will cease to exist. Either way, moving to containers is going to make managing dependency nightmares like this easier.
