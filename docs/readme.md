# Site Structure & Wagtail Classes

_Note_: as of right now, this is just a sketch based on what we assume to be true. We still need to implement all the page types.

There are a few layers to the CCA Libraries site:

```
home page (root)
|---services landing page
    |---service page
|---collections landing page¹
|---about us landing page
    |---policy/about us page
    |---blog page²
```

The service, policy/about us, and blog child-of-child pages all may be able to share a single template since they should be primarily text but with perhaps one main image and a few inline images. We can use one `ContentPage` class to cover all of them, perhaps.

The landing pages almost certainly will require distinct templates.

<sup>1</sup>We might not need a subpage type for collections since the collections will link out to an external resource.

<sup>2</sup>See [wagtail-blog-app](https://github.com/Tivix/wagtail-blog-app) for resources on building this app. Also, note that _we do not need a Blog Index_ page type or template with our current design as their is no blog index, merely a list of adjacent posts in a sidebar.

## Class Names

Again, these are conjectural, not set in stone.

`HomePage`, `ServicesPage`, `CollectionsPage`, `AboutUsPage`, `ContentPage` (covering all child-of-child pages).
