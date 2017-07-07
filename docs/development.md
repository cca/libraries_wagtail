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
> npm run sass-watch
```
