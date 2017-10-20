# Libraries' News (Blog)

A simple blog app for writing news/announcement type content. The latest two posts published here are shown on the home page. All content under the /news/ section of the site comes from this app.

There is a blog index page, but it is created automatically via migration and is a singleton. The way Wagtail's page hierarchy works, we need a shared parent for all the posts. When the slug for the index is visited, the most recent post is rendered. The index does not have a template.

The blog post body reuses all of the streamfield blocks defined in the `categories` app's models.py with SASS styles under the main `libraries` app. Hence changes to the streamfields' definitions will result in migrations within this app.

There were issues when building dev sites or previewing blog pages with some blog app code that assumes that posts exist. If there are no posts, some code may throw index errors e.g. `all_blog_posts` has nothing in it.

## Import

There is an `import_blogs` management command which is used to import blog posts from a CSV file. Included is a "test_import.csv" file for testing the command, it generates a "Test Blog Post Import" post. There's also a SQL query "drupal_blog_extract.sql" for pulling the required fields from our old Drupal 6 blog. Do not use the management command without reading through the script first; there are some issues with it and it was really meant to only be run once.
