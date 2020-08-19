# Site Structure & Wagtail Classes

There are a few layers to the CCA Libraries site. The outline below shows the basic structure with a few annotations:

- The parentheses next to a page's title contain the name of its model
- An asterisk \* denotes a _singleton_ page (e.g. the home page, various indices)
- A caret ^ denotes non-page content (doesn't appear in search results, shouldn't be visited directly in a web browser)

```
Root (Wagtail abstraction)
    |---Home* (home.HomePage)
        |---Services* (categories.CategoryPage)
            |---Instructional Services & Technology^ (categories.RowComponent)
                |---Child content pages...
            |---Circulation Services^ (categories.RowComponent)
                |---Child content pages...
            |---Emerging Projects^ (categories.RowComponent)
                |---Child content pages...
        |---Collections* (categories.CategoryPage)
            |---Collections^ (categories.RowComponent)
                |---Various special collections (categories.SpecialCollectionsPage)
                |---Child content pages...
        |---About Us* (categories.CategoryPage)
            |---About Us^ (categories.RowComponent)
                |---Staff listing* (staff.StaffListPage)
                |---Hours* (hours.HoursPage)
                |---Child content pages...
        |---Blog*^ (blog.BlogIndex)
            |---All blog posts... (blog.BlogPage)
        |---Exhibits* (exhibitions.ExhibitsIndexPage)
            |---All digital exhibitions... (exhibitions.ExhibitPage)
        |---Search (no model, only a view in search/views.py)
        |---Brokenlinks^ (no model, only a view in brokenlinks/views.py)
        |---Instagram^ (instagram.Instagram, used on home page)
        |---Serials Solution API^ (no model, only a view in sersol_api/views.py)
```

The grandchild pages of each main category (Services, Collections, and About Us), represented above with the phrase "child content pages...", can use one of three page models: ServicePage, AboutUsPage, and SpecialCollectionsPage. Each of these pages can then, in turn, have children of any of those three types.

## Class Names

Class names of various page models, even singleton ones like the blog index.

`home.HomePage`, `categories.CategoryPage`, `categories.RowComponent`, `categories.AboutUsPage`, `categories.ExternalLink`, `categories.ServicePage`, `categories.SpecialCollectionsPage`, `blog.BlogIndexPage`, `blog.BlogPage`, `hours.HoursPage`, `staff.StaffListPage`, `exhibitions.ExhibitsIndexPage`, `exhibitions.ExhibitPage`.

## Static Files

We put _all_ static (CSS, JS) files under the main app's static folder, in libraries/libraries/static. I am not sure if this is a great strategy as it separates apps from their styles (e.g. libraries/exhibitions from libraries/libraries/static/scss/exhibits.scss).

There are two empty folders under the main static directory ("moodle" and "summmon") for hosting static files used in external services that cannot host their own content. These files are generated in separate projects, see the CCA GitHub to find them.
