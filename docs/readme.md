# Site Structure & Wagtail Classes

_Note_: as of right now, this is just a sketch based on what we assume to be true. We still need to implement all the page types.

There are a few layers to the CCA Libraries site:

home page (root)
|---services landing page
    |---service page
|---collections landing page*
|---about us landing page
    |---policy/about us page
    |---blog page

The service, policy/about us, and blog child-of-child pages all may be able to share a single template since they should be primarily text but with perhaps one main image and a few inline images. We can use one `ContentPage` class to cover all of them, perhaps.

The landing pages almost certainly will require distinct templates.

\*We might not need a subpage type for collections since the collections will link out to an external resource.

## Class Names

Again, these are conjectural, not set in stone.

`HomePage`, `ServicesPage`, `CollectionsPage`, `AboutUsPage`, `ContentPage` (covering all child-of-child pages).
