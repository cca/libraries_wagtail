$(function(){
    $('#id_exhibit_artwork-FORMS').change('.js-type ', ev => {
        let select = $(ev.target).find('select')
        let type = select.val()
        let fields = select.parents('ul.fields')

        if (type === 'audio') {
            fields.find('.js-embed_code').hide()
            fields.find('.js-media').show()
            fields.find('.js-image').addClass('required')
        } else if (type === 'html') {
            fields.find('.js-embed_code').show()
            fields.find('.js-media').hide()
            // only type for which we don't require an image & we may change that
            fields.find('.js-image').removeClass('required')
        } else if (type === 'image') {
            fields.find('.js-embed_code').hide()
            fields.find('.js-media').hide()
            fields.find('.js-image').addClass('required')
        } else if (type === 'video') {
            fields.find('.js-embed_code').hide()
            fields.find('.js-media').show()
            fields.find('.js-image').addClass('required')
        }
    })

    // trigger the above logic on page load
    $('#id_exhibit_artwork-FORMS .js-type').trigger('change')

    // auto-tag images with the slugified title of the exhibition
    // fires whenever we're on the "Upload" tab
    $(document).on('click', '.modal-content a[href="#upload"]', () => {
        var title = $('#id_title').val()
        // handy URLify function is already present
        $('#id_tags').tagit('createTag', URLify(title))
    })
})
