// use libraryh3lp Presence API https://dev.libraryh3lp.com/presence.html
fetch('https://libraryh3lp.com/presence/jid/cca-libraries-queue/chat.libraryh3lp.com/text')
    .then(resp => resp.text())
    .then(status => {
        // only display if we are signed in
        if (status == 'available' || status == 'chat') {
            $('body').append('<div class="needs-js">')
            var x = document.createElement("script"); x.type = "text/javascript"; x.async = true;
            x.src = (document.location.protocol === "https:" ? "https://" : "http://") + "libraryh3lp.com/js/libraryh3lp.js?13843";
            var y = document.getElementsByTagName("script")[0]; y.parentNode.insertBefore(x, y);
        }
    })
