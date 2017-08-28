fetch('http://127.0.0.1:8000/hours/?format=json')
    .then(response => response.json())
    .then(data => {
        // meyer
        let meyer = document.createElement('p').innerText = data.Meyer + '  today'
        document.querySelectorAll('.footer-section__site')[0].append(meyer)
        // simpson
        let simpson = document.createElement('p').innerText = data.Simpson + ' today'
        document.querySelectorAll('.footer-section__site')[1].append(simpson)
    })
