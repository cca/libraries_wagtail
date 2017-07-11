# Development

TODO: write out a thorough development workflow for documenting, writing, and pushing to production changes to the site.

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

We're using [Gulp](http://gulpjs.com/) for our front-end build tool because that was what Torchbox's designer used, but could easily switch to something else. Note that tools like autoprefixer are solving some bugs though so switching might result in some style problems (e.g. the radio buttons on the home page search box need autoprefixer).
