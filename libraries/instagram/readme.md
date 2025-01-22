# Instagram

Pulls the latest Instagram post for an account, which is then used on the home page. Instagram has changed their underlying API _many_ times on us, necessitating repeated rewrites of this code. For now, we are pulling JSON straight from Instagram without using an API (see [#168](https://github.com/cca/libraries_wagtail/issues/166)).

We should consider a way to disable this app and display something else on the home page (a random image?), for periods when it breaks and we won't be able to fix it in a timely manner.

Posts are retrieved using the `instagram` management command, e.g. `python manage.py instagram`. This command runs on a daily schedule in a cron job (see the `instagram` cronjob in [production.yaml](../../kubernetes/production.yaml)).

## Configuration

Go to Admin > Settings > Instagram settings. The Instagram app ID came from [this blog post](https://scrapfly.io/blog/how-to-scrape-instagram/) and supposedly "doesn't change often". If it does, update this configuration value. The username is just our Instagram username. Note that changing the username here won't replace all our images from Instagram, it just means the next ones being added will come from a different username. Choosing a private account will result in an error.
