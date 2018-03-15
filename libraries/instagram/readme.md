# Instagram

Pulls the latest Instagram post for an account, which is then used on the home page. This doesn't make any attempt to see if we already have the latest Instagram, it just mindlessly pulls down the latest one, so we end up with a lot of dupes in the database but it doesn't matter because only the latest one displays.

Set up:

- create an [Instagram API client](https://www.instagram.com/developer/clients/manage/) & get an [access token](https://www.instagram.com/developer/authentication/) for the account you want to display
- add the access token to the `INSTAGRAM_ACCESS_TOKEN` setting
- run the management command, `python manage.py instagram`, to pull down the latest Instagram post
- set up a cron job to run the management command above on a schedule

Previously, we attemped to use the undocumented https://www.instagram.com/ccalibraries/media/ and https://www.instagram.com/ccalibraries/?__a=1 URLs which returned JSON data about our Instagram account. But after multiple unannounced changes to the structure of this data, it was clear that using the Instagram API was a better decision. Unfortunately, Instagram is about to migrate to the Instagram Graph API and it sounds like it's only available for "business accounts" so it's unclear how easily we'll be able to do the same thing with the new API. But the one we're using currently should be functional until "early 2020".
