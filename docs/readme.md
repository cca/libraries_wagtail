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
            |---Instructional Technology & Information Literacy^ (categories.RowComponent)
                |---Child content pages...
            |---Circulation Services^ (categories.RowComponent)
                |---Child content pages...
        |---Collections* (categories.CategoryPage)
            |---Collections^ (categories.RowComponent)
                |---Special Collections (categories.SpecialCollectionsPage)
                |---Child content pages...
        |---About Us* (categories.CategoryPage)
            |---About Us^ (categories.RowComponent)
                |---Staff listing (staff.StaffListPage)
                |---Hours (hours.HoursPage)
                |---Child content pages...
        |---Blog*^ (blog.BlogIndex)
            |---All blog posts... (blog.BlogPage)
        |---Search (no model, search() in search/views.py is the view)
```

The grandchild pages of each category (Services, Collections, and About Us), represented above with the phrase "child content pages...", can use one of three page models: ServicePage, AboutUsPage, and SpecialCollectionsPage. Each of these pages can then, in turn, have children of any of those three types.

## Class Names

Again, these are conjectural, not set in stone.

`home.HomePage`, `categories.CategoryPage`, `categories.RowComponent`, `categories.AboutUsPage`, `categories.ServicePage`, `categories.SpecialCollectionsPage`, `blog.BlogPage`, `hours.HoursPage`, `staff.StaffListPage`.
