# Instagram

Pulls the latest Instagram post for an account, which is then used on the home page. This uses the `v1/users/self/media/recent` API ([dox](https://www.instagram.com/developer/endpoints/users/#get_users_media_recent_self)) and merely grabs the latest post available.

Configuration:

- create an [Instagram API client](https://www.instagram.com/developer/clients/manage/) so you can get a client ID and set a redirect_uri
- add both `INSTAGRAM_CLIENT_ID` and `INSTAGRAM_REDIRECT_URI` to your settings
- run the management command, `python manage.py get_oauth_token`, copy the "access_token" parameter out of the redirect URI, then paste that back into the command prompt to save it to the database
- now when you run `python manage.py instagram` the latest gram is saved to the database
- set up a cron job to run the management command above on a schedule

See IG's [authentication](https://www.instagram.com/developer/authentication/) page for more. I couldn't think of an elegant way to automate renewing the token without human intervention—someone has to physically click a button on Instagram to trigger the redirect. For now, the best we can do is log an error when the OAuth token is out of date, then use `get_oauth_token` to get a new one.

Previously, we attempted to use the undocumented https://www.instagram.com/ccalibraries/media/ and https://www.instagram.com/ccalibraries/?__a=1 URLs which returned JSON data about our Instagram account. But after multiple unannounced changes to the structure of this data, it was clear that using the Instagram API was a better decision. Unfortunately, Instagram is about to migrate to the Instagram Graph API and it sounds like it's only available for "business accounts" so it's unclear how easily we'll be able to do the same thing with the new API. But the one we're using currently should be functional until "early 2020".
