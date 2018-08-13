$(function(){
    $('#id_exhibit_artwork-FORMS').change('.js-type', ev => {
        let select = $(ev.target)
        let type = $(select).val()
        let form = $(select).prevUntil('ul.fields')

        if (type == 'audio') {
            $('.js-media').show()
            $('.js-embed_code').hide()
        } else if (type === 'html') {
            $('.js-embed_code').show()
            $('.js-media').hide()
        } else if (type === 'image') {
            $('.js-media').hide()
            $('.js-embed_code').hide()
        } else if (type === 'video') {
            $('.js-media').show()
            $('.js-embed_code').hide()
        }
    })
})
