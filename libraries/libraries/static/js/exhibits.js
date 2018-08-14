// exhibits app code, mostly lightGallery.js edits
$(() => {
    $('.js-masonry').masonry({
        "columnWidth": 600,
        "fitWidth": true,
        "gutter": 4,
        "itemSelector": ".js-gallery--work"
    })

    let options = {
        hideBarsDelay: 3000,
        selector: '.js-gallery--work',
        subHtmlSelectorRelative: true,
        vimeoPlayerParams: {
            byline: false,
            portrait: false,
            title: false
        }
    }
    let $lg = $('.js-lightgallery').lightGallery(options);

    $lg.on('onAfterAppendSubHtml.lg', (event, index) => {
        let slide = $('.js-gallery--work').eq(index)
        let zooms = $('#lg-zoom-in, #lg-zoom-out, #lg-actual-size')
        let linked_title = $('.js-linked-title')

        // only show zoom functions for images
        if (slide.find('.gallery--work__image').length > 0) {
            zooms.show()
        } else {
            zooms.hide()
        }
    })
})
