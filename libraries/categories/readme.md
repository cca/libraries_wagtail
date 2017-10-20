# Categories a.k.a. cats :cat: :cat: :cat:

This is an important app which contains the majority of content of the site. Other than the blog and a few one-off pages (e.g. Staff and Hours), most pages are instances of the models defined here.

The "categories" themselves are the three main sections of the site: Services, Collections, and About Us. There exists one instance of a `CategoryPage` for each of those, then one to many `RowComponent`s beneath them, and then beneath those a plethora of content pages which use the models defined here (`AboutUsPage` a.k.a. "Simple text page", `ServicePage` a.k.a. "Complex text page" which is the most commonly used, and `SpecialCollectionsPage`). Pages from other apps such as Hours or Staff also exist with the Categories portion of the site's hierarchy. Finally, there is also an `ExternalLink` model for linking to external sites while placing the content within our site hierarchy (e.g. a link to the library catalog underneath Collections).

**A note on model names**: Originally, I had thought that the pages under each category would use a template specific to that category, thus the `AboutUsPage` and `ServicePage` names. This never came about and those templates are not tied to particular categories but rather represent simple (no streamfields) or more complicated (choice of several blocks) page design options. The ServicePage itself is not really a template created by Torchbox but a modification of the blog post template, thus why the HTML in the blocks used on that page all bear class names prefixed with `blog-post__`.

## Blocks

This app is also important because it contains the HTML templates and model definitions for the streamfield blocks which are reused elsewhere, for instance in the blog app. The SASS styles for these blocks, however, live with all other styles under the main Libraries app.
