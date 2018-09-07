// exhibits app code, mostly lightGallery.js edits
$(() => {
    let gallery = $('.js-masonry')
    gallery.imagesLoaded(() => {
        gallery.masonry({
            "columnWidth": 600,
            "fitWidth": true,
            "gutter": 4,
            "itemSelector": ".js-gallery--work"
        })
    })

    let options = {
        autoplayFirstVideo: false,
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

    $lg.on('onAfterOpen.lg', () => {
        // add missing tooltips for lightGallery controls
        ['zoom-in', 'zoom-out', 'actual-size', 'download'].forEach(action => {
            $('#lg-' + action).attr('title', action.replace('-', ' '))
        })
    })

    $lg.on('onAfterAppendSubHtml.lg', (event, index) => {
        let slide = $('.js-gallery--work').eq(index)
        let zooms = $('#lg-zoom-in, #lg-zoom-out, #lg-actual-size')

        // only show zoom functions for images
        if (slide.find('.gallery--work__image').length > 0) {
            zooms.show()
        } else {
            zooms.hide()
        }
    })
})
