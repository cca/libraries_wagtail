fetch('http://127.0.0.1:8000/hours/?format=json')
    .then(response => response.json())
    .then(data => {
        let h = function (selector, datum='closed') {
            let el = document.querySelector(selector)
            if (el) el.innerText = datum
        }

        // info box hours
        h('.home-info-box-times__timetable-times.js-simpson', data.Simpson)
        h('.home-info-box-times__timetable-times.js-meyer', data.Meyer)
        h('.home-info-box-times__timetable-times.js-materials', data.materials)

        // footer hours
        h('.footer-section__site-address.js-meyer-hrs', data.Meyer + ' today')
        h('.footer-section__site-address.js-simpson-hrs', data.Simpson + ' today')
    })
