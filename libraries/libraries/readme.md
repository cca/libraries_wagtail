# CCA Libraries Wagtail

This is the main Django app which contains the backbone of our Wagtail site. It has these vitally important resources:

- settings/configuration for the whole site
- the urls.py (router) file
- _all_ the static files
    + fonts
    + images
    + JavaScript
    + SASS (compiled CSS, too)
- base HTML templates including universal header/footer/search
- API settings
- custom filters for loggers
- our custom view for serving documents
- robots.txt

What _isn't_ stored here? The `categories` app has quite a few vitally important features of the site, such as the models and templates for reusable blocks of content. Management commands apparently cannot be placed under the primary app so they also live under various other apps. Finally, our custom template tags live in the `home` app.
