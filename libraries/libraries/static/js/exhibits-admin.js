$(function(){
    $('#id_exhibit_artwork-FORMS').on('change', '.js-type', ev => {
        let select = $(ev.currentTarget).find('select')
        let type = select.val()
        let fields = select.parents('ul.fields')

        // required/unneeded fields logic for different work types
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

    // when a new artwork is added, trigger its change event to enforce logic
    $('#id_exhibit_artwork-ADD').on('click', () => {
        $('li[id^=inline_child_exhibit_artwork-]').last()
            .find('.js-type').trigger('change')
    })

    // auto-tag images with the slugified title of the exhibition
    // fires whenever we're on the "Upload" tab
    $(document).on('click', '.modal-content a[href="#upload"]', () => {
        var title = $('#id_title').val()
        // handy URLify function is already present
        $('#id_tags').tagit('createTag', URLify(title))
    })

    // make search description appear required (does not actually force requirement)
    $('#id_search_description').attr('required', true).closest('li').addClass('required')
})
