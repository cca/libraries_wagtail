# Site Structure & Wagtail Classes

_Note_: This is still just a sketch. Expect things to be in flux until the site goes live.

There are a few layers to the CCA Libraries site. The outline below shows the basic structure with a few annotations:

- The parenthesis next to a page title contain the name of its model
- An asterisk \* denotes a _singleton_ page
- A caret ^ denotes non-page content (doesn't appear in search results, shouldn't be visited directly)

```
Root (Wagtail abstraction)
    |---Home (home.HomePage)
        |---Services* (categories.CategoryPage)
            |---All service pages...
        |---Collections* (categories.CategoryPage)
            |---Special Collections (categories.SpecialCollectionsPage)
            |---All collection pages...
        |---About Us* (categories.CategoryPage)
            |---Staff listing
            |---Hours
            |---All policy pages...
        |---Blog*^ (blog.BlogIndex)
            |---All blog posts... (blog.BlogPage)
        |---Search (no model, search() in search/views.py is the view)
```

## Class Names

Again, these are conjectural, not set in stone.

`HomePage`, `ServicesPage`, `CollectionsPage`, `AboutUsPage`, `ContentPage` (covering both services & about us grandchild pages), `BlogPage`.
