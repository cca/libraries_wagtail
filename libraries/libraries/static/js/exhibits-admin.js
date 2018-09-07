$(function(){
    $('#id_exhibit_artwork-FORMS').change('.js-type', ev => {
        let select = $(ev.target)
        let type = select.val()
        let form = select.parents('ul.fields')

        if (type === 'audio') {
            form.find('.js-embed_code').hide()
            form.find('.js-media').show()
            form.find('.js-image').addClass('required')
        } else if (type === 'html') {
            form.find('.js-embed_code').show()
            form.find('.js-media').hide()
            // only type for which we don't require an image & we may change that
            form.find('.js-image').removeClass('required')
        } else if (type === 'image') {
            form.find('.js-embed_code').hide()
            form.find('.js-media').hide()
            form.find('.js-image').addClass('required')
        } else if (type === 'video') {
            form.find('.js-embed_code').hide()
            form.find('.js-media').show()
            form.find('.js-image').addClass('required')
        }
    })
})
