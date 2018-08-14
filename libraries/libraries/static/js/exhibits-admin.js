$(function(){
    $('.js-media').hide()

    $('#id_exhibit_artwork-FORMS').change('.js-type', ev => {
        let select = $(ev.target)
        let type = $(select).val()
        let form = $(select).prevUntil('ul.fields')

        if (type == 'audio') {
            $('.js-embed_code').hide()
        } else if (type === 'html') {
            $('.js-embed_code').show()
        } else if (type === 'image') {
            $('.js-embed_code').hide()
        } else if (type === 'video') {
            $('.js-embed_code').hide()
        }
    })
})
