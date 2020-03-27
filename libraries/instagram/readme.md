# Instagram

Pulls the latest Instagram post for an account, which is then used on the home page. This uses the Instagram Basic Display API ([dox](https://developers.facebook.com/docs/instagram-basic-display-api/getting-started)) and merely grabs the latest post available.

Configuration ([these steps are a good outline](https://developers.facebook.com/docs/instagram-basic-display-api/getting-started)):

- create a Facebook app on https://developers.facebook.com
- add the **Instagram** product, select "Basic Display" > **Create new app**
- Fill out all the fields, though we won't use many of them. We don't have a script that programmatically uses the redirect URI; I just manually copy the code out of the URL. Note that redirect URIs apparently cannot be a straight domain like http://example.com (Facebook will append a slash like `.com/` without telling you).
- add an "Instagram Test User" for the Instagram account you want to display
- add the app's `INSTAGRAM_CLIENT_ID`, `INSTAGRAM_CLIENT_SECRET`, and `INSTAGRAM_REDIRECT_URI` to your settings
- run the management command, `python manage.py get_oauth_token`, copy the "code" parameter out of the redirect URI (**IMPORTANT**: remove the `#\_` at the end), then paste that back into the command prompt
- the script will complete a couple steps to get an OAuth access token
- now when you run `python manage.py instagram` the latest gram is saved to the database
- set up a cron job to run the management command above on a schedule

This whole setup process should only need to run once. Once we obtain an access token it lasts for sixty days and can be [exchanged for a fresh token](https://developers.facebook.com/docs/instagram-basic-display-api/guides/long-lived-access-tokens) which also lasts that long, meaning that the app can keep checking the expiration date and refreshing its token during a routine `python manage.py instagram` cron job.

Previously, we attempted to use the undocumented https://www.instagram.com/ccalibraries/media/ and https://www.instagram.com/ccalibraries/?__a=1 URLs which returned JSON data about our Instagram account. But after multiple unannounced changes to the structure of this data, it was clear that using the (now defunct) Instagram API was a better decision. Unfortunately, Instagram then migrated to the Instagram Graph API which required us to rewrite the whole authentication portion of this app for a second time.
