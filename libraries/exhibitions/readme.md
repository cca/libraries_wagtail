# Exhibitions

A new content type and template for representing _online_ exhibitions. The Exhibitions app should most closely resemble the Blog app in that its content will also live in a separate tree outside the Categories hierarchy. The template will diverge further from all other content types since we truly want to highlight the _nature_ of the exhibition and its objects. The header, footer, and other features intended to make the main site more navigable are less important for this app.

# lightGallery.js

The Exhibitions gallery of works uses [lightGallery](http://sachinchoolur.github.io/lightGallery) for a fullscreen image viewer. The style our our gallery has been modified a bit in static/scss/components/exhibits/\_lightgallery.scss.

[Masonry](https://masonry.desandro.com/) is used for the tiled layout of the gallery, since we cannot do a static layout given the variable sizes of art works. Since the layout won't work well without knowing the sizes of images, we use [imagesLoaded](https://imagesloaded.desandro.com/) to initialize the layout only after images have been downloaded to the browser.
