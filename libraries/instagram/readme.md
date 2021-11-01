# Instagram

Pulls the latest Instagram post for an account, which is then used on the home page. This uses the Instagram Basic Display API ([dox](https://developers.facebook.com/docs/instagram-basic-display-api/getting-started)) and merely grabs the latest post available.

Configuration ([these steps are a good outline](https://developers.facebook.com/docs/instagram-basic-display-api/getting-started)):

- create a Facebook app on https://developers.facebook.com
- add the **Instagram** product, select "Basic Display" > **Create new app**
- Fill out all the fields, though we won't use many of them. We don't have a script that programmatically uses the redirect URI; I just manually copy the code out of the URL. Note that redirect URIs apparently cannot be a straight domain like http://example.com (Facebook will append a slash like `.com/` without telling you).
- add an "Instagram Test User" for the Instagram account you want to display
- add `INSTAGRAM_REDIRECT_URI` to your settings
- create k8s secrets that populate `INSTAGRAM_APP_ID` and `INSTAGRAM_SECRET` env vars (see section below)
- run the management command, `python manage.py get_oauth_token`, copy the "code" parameter out of the redirect URI, then paste that back into the command prompt
- the script completes a couple steps to get an OAuth access token
- (optionally) create an image Collection named "Instagram" to hold downloaded images
- now when you run `python manage.py instagram` the latest gram is saved to the database
- set up a cron job to run the management command above on a schedule

This whole setup process should only need to run once. Once we obtain an access token it lasts for sixty days and can be [exchanged for a fresh token](https://developers.facebook.com/docs/instagram-basic-display-api/guides/long-lived-access-tokens) which also lasts that long, meaning that the app can keep checking the expiration date and refreshing its token during a routine `python manage.py instagram` cron job.

Previously, we attempted to use the undocumented https://www.instagram.com/ccalibraries/media/ and https://www.instagram.com/ccalibraries/?__a=1 URLs which returned JSON data about our Instagram account. But after multiple unannounced changes to the structure of this data, it was clear that using the (now defunct) Instagram API was a better decision. Unfortunately, Instagram then migrated to the Instagram Graph API which required us to rewrite the whole authentication portion of this app for a second time.

## Editing Secrets in Kubernetes

We no longer use local Django settings for secrets like the Instagram Facebook app's credentials, we use [kubernetes secrets](https://kubernetes.io/docs/concepts/configuration/secret/). Secrets contain key-value data pairs where the value is base64 encoded. In the steps below, `k` is an alias for `kubectl -n$NAMESPACE` where `NAMESPACE` is one of our staging, development, or production namespaces.

**list existing secrets** `k get secrets`

**view a specific secret** `k get secret $SECRET_NAME`

**view $KEY's (decoded) data from $SECRET_NAME** `k get secret $SECRET_NAME -o jsonpath='{.data.$KEY}' | base64 --decode`

**edit a secret** `k edit secret $SECRET_NAME`

If you want to edit a value, you must base64 encode it. Kubernetes will not let you save the secret otherwise and will not automatically decode or encode strings for you. The easiest way to edit values is to copy a base64-encoded string onto your clipboard, then paste it in your text editor: `echo $VALUE | base64 | pbcopy && k edit secret $SECRET_NAME`

Once a secret is properly configured in a staging or development namespace, remember that it must be copied to production. You can copy a secret by writing it to a file, stripping instance-specific data (all datetimes like created or last modified, any namespace values), then creating the secret in production: `kubectl -n$STAGING get secret $NAME -o yaml > $NAME.yaml && vim $NAME.yaml && kubectl -n$PRODUCTION create -f $NAME.yaml`
