# Instagram

Pulls the latest Instagram post for an account, which is then used on the home page. This doesn't make any attempt to see if we already have the latest Instagram, it just mindlessly pulls down the latest one, so we end up with a lot of dupes in the database but it doesn't matter because only the latest one displays.

Configuration:

- create an [Instagram API client](https://www.instagram.com/developer/clients/manage/) so you can get a client ID and set a redirect redirect_uri
- add both `INSTAGRAM_CLIENT_ID` and `INSTAGRAM_REDIRECT_URI` to your settings
- run the management command, `python manage.py get_oauth_token`, copy the "access_token" parameter out of the redirect URI, then paste that back into the command prompt to save it to the database
- now when you run `python manage.py instagram` the latest gram is saved to the database
- set up a cron job to run the management command above on a schedule

See IG's [authentication](https://www.instagram.com/developer/authentication/) page for more. I couldn't think of an elegant way to automate renewing the token without human intervention—someone has to physically click a button on Instagram to trigger the redirect. So for now the best we can do is log an error when the OAuth token is out of date, then use `get_oauth_token` to get a new one.

Previously, we attempted to use the undocumented https://www.instagram.com/ccalibraries/media/ and https://www.instagram.com/ccalibraries/?__a=1 URLs which returned JSON data about our Instagram account. But after multiple unannounced changes to the structure of this data, it was clear that using the Instagram API was a better decision. Unfortunately, Instagram is about to migrate to the Instagram Graph API and it sounds like it's only available for "business accounts" so it's unclear how easily we'll be able to do the same thing with the new API. But the one we're using currently should be functional until "early 2020".
