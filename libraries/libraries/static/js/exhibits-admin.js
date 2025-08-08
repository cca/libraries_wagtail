$(() => {
    // required/unneeded fields logic for different work types
    function requireInput(selector, required = true) {
        if (required && !$(selector).find('.w-required-mark').length) {
            $(selector).find('label').append('<span class="w-required-mark">*</span>')
        }
        if (!required) $(selector).find('label').find('.w-required-mark').remove()
    }

    $('#id_exhibit_artwork-FORMS').on('change', '.js-type', ev => {
        let select = $(ev.currentTarget).find('select')
        let type = select.val()
        console.log(`type change, new type ${type}`)
        let fields = select.parents('.w-panel__content[id^="inline_child_exhibit_artwork"]')
        // we require images for all types except HTML embed
        requireInput('.js-image')

        if (type === 'audio') {
            fields.find('.js-embed_code').hide()
            fields.find('.js-media').show()
            requireInput('.js-media')
        } else if (type === 'html') {
            fields.find('.js-embed_code').show()
            fields.find('.js-media').hide()
            requireInput('.js-image', false)
        } else if (type === 'image') {
            fields.find('.js-embed_code').hide()
            fields.find('.js-media').hide()
        } else if (type === 'video') {
            fields.find('.js-embed_code').hide()
            fields.find('.js-media').show()
            requireInput('.js-media')
        }
    })

    // trigger the above logic on page load & when new works are added
    $('#id_exhibit_artwork-FORMS .js-type').trigger('change')
    $('#id_exhibit_artwork-ADD').on('click', () => {
        $('[id^=inline_child_exhibit_artwork-]').last()
            .find('.js-type').trigger('change')
    })

    // auto-tag images with the title of the exhibition
    // fires whenever we're on the image "Upload" tab of an exhibit
    if ($('#id_exhibit_artwork-FORMS').length) {
        $(document).on('click', '#tab-label-upload', () => {
            // select "Exhibitions Media" collection (ID = 7)
            $('#id_image-chooser-upload-collection').val("7")
            var title = `"${$('#id_title').val().trim()}"`
            // instantiate tagit first, for some reason it's often not ready
            if (title) $('.tagit').tagit().tagit("createTag", title)
        })
    }
})
