document.querySelectorAll('a[href^="/documents/"]').forEach(a => {
    a.addEventListener('click', ev => {
        let u = new URL(a.href)
          , path = u.pathname.split('/')
          , id = path[2]
          , name = path[3]
        ga('send', 'event', 'download', id, name)
    })
});
