(function() {

function ccaCustomizations() {
    const d = document
    const css = d.createElement('link')
    css.setAttribute('rel', 'stylesheet')
    css.setAttribute('type', 'text/css')
    css.href = 'https://libraries.cca.edu/static/summon/summon.css'
    // load CSS adjustments
    d.querySelector('head').append(css)

    // adjust main logo size/spacing on large screens
    d.querySelector('div[size="large"] .logo')
        .setAttribute('src', 'https://libapps.s3.amazonaws.com/sites/2210/banner/libguide-logo-fa17.png')
}

ccaCustomizations()
// defined in broken-link-modal.js
brokenLinkReports()

})();
