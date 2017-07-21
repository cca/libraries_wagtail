# Development

Basic outline for working on the site:

- Pick an app or feature to work on & checkout a logically-named branch
- If model or database changes happen, run `makemigrations`
- Feel free to `git push origin $BRANCH` to get the changes on GitHub but _don't push to master_ until the changes have been tested on another copy of the site
- Check the readme here to see if models or class names have to be updated

## Shell Commands

These should be run from inside the "libraries" directory as it is the root of the Wagtail site.

```sh
> # update database schema—run after any change to a model
> python manage.py makemigrations; python manage.py migrate
> # run a local development server
> python manage.py runserver
> # rebuild the site styles from SASS
> npm run sass
> # continually watch for SASS changes & recompile the CSS
> npm run watch
```

W use [Gulp](http://gulpjs.com/) for our front-end build tool because that was what Torchbox's designer used, but could easily switch to something else. Note that tools like autoprefixer are solving some bugs though so switching might result in some style problems (e.g. the radio buttons on the home page search box need autoprefixer).

## Migration Tricks

Sometimes when we create a model, we want to immediately create an instance of it rather than require the admin to create one manually. This lets us create things like the home page or top-level categories programmatically, greatly decreasing the time to bootstrap a new iteration of the site. Here are a couple examples of this tactic:

- home/migrations/0002_create_homepage.py
- blog/migrations/0003_create_blogindex.py
- categories/migrations/0006_create_categories.py

**Notes:**

- if you're going to generate child pages, make sure the migration lists the migration generating the parent page as a dependency (see how create_categories depends upon create_homepage)
- we can disallow certain page types from being created manually at all if we a) generate them during migrations and b) ensure no other model lists them in its `subpage_types`
- `slug`s must be unique & therefore make a good hook when writing the `remove_xxx` method which undoes the effects of the migration
