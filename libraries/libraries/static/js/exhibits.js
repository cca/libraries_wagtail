// exhibits app code, mostly lightGallery.js edits
$(() => {
    // Masonry.js https://masonry.desandro.com
    // Options are declared in a data attribute on this element
    let gallery = $('.js-masonry')
    gallery.imagesLoaded(() => gallery.masonry())

    let lgOptions = {
        autoplayFirstVideo: false,
        hideBarsDelay: 3000,
        selector: '.js-gallery--work',
        subHtmlSelectorRelative: true,
        // video player settings
        // showinfo & rel settings can no longer make the embedded player
        // minimalist so I think we should just show the controls
        // https://developers.google.com/youtube/player_parameters
        youtubePlayerParams: {
            disablekb: 1,
            modestbranding: 1
            // origin: location.hostname
        },
        // note that many Vimeo videos override whatever defaults we request
        // https://developer.vimeo.com/api/oembed/videos
        vimeoPlayerParams: {
            byline: 0,
            // leave '#' off color hex code
            color: '17bfb3',
            dnt: 1,
            portrait: 0,
            title: 0
        }
    }
    // special handling for embedded videos
    $('.js-gallery--work[data-iframe]').each((idx, el) => {
        let re = /(youtube\.com|youtu\.be|vimeo\.com)/
        let $el = $(el)
        let src = $el.data('src')
        // remove data-iframe from embeds that look like YouTube or Vimeo
        if (src.match(re)) $el.removeAttr('data-iframe')
    })
    let lg = $('.js-lightgallery').lightGallery(lgOptions)

    lg.on('onAfterOpen.lg', () => {
        // add missing tooltips for lightGallery controls
        ['zoom-in', 'zoom-out', 'actual-size', 'download'].forEach(action => {
            $('#lg-' + action).attr('title', action.replace('-', ' '))
        })
    })

    lg.on('onAfterAppendSubHtml.lg', (event, index) => {
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
