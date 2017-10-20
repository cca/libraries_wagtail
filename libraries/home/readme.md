# Home Page

The home page app, designed for a solitary page which is a child of Wagtail's root and parent to all other content.

The home page does have some content, including an editable background image, image attribution, and a few text blurbs, but it is complicated enough to demand its own app primarily because of the way it interfaces with other applications. The Home app pulls hours data from the Hours app, our latest Instagram post from the Instagram app, and our latet two blog posts from the Blog app.

## Management Commands

Because the main app of a Wagtail instance cannot host management commands, the Home app is the destination for generic commands which don't belong under a particular app. Thus why the `import_redirects` and `pw_reset` tools live here.

**import_redirects** — this takes a CSV of URL redirects and creates them in Wagtail. You can use the includede "drupal_path_redirect.sql" to extract redirects from Drupal 6.

**pw_reset** — this is used when syncing a dev environment with the production database and media. I don't want to store (even hashed) versions of people's passwords so my sync script erases everyone's passwords after users have been imported.

Generic wagtail hooks are also defined in this app.
