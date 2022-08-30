fetch('/hours/?format=json')
    .then(response => response.json())
    .then(data => {
        const h = (selector, datum='closed') => {
            let el = document.querySelector(selector)
            if (el) el.innerText = datum
        }

        // info box hours
        h('.home-info-box-times__timetable-times.js-simpson', data.Simpson)
        h('.home-info-box-times__timetable-times.js-materials', data.Materials)

        // footer hours
        h('.footer-section__site-address.js-simpson-hrs', data.Simpson + ' today')
        h('.footer-section__site-address.js-matlib-hrs', data.Materials + ' today')
    });
