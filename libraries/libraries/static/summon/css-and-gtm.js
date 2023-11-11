(function() {

function ccaCustomizations() {
    let d = document
    let css = d.createElement('link')
    css.setAttribute('rel', 'stylesheet')
    css.setAttribute('type', 'text/css')
    css.href = 'https://libraries.cca.edu/static/summon/summon.css'
    // load CSS adjustments
    d.querySelector('head').append(css)

    // adjust main logo size/spacing on large screens
    const logo = d.querySelector('div[size="large"] .logo')
    if (logo) logo.setAttribute('src', 'https://libapps.s3.amazonaws.com/sites/2210/banner/libguide-logo-fa17.png')
}

function main() {
    ccaCustomizations()
    // defined in broken-link-modal.js
    brokenLinkReports()
}

// logo is loaded asynchronously, so wait for it to appear
setTimeout(main, 500)

})();
