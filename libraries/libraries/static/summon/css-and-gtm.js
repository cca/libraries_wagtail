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
    d.querySelector('div[size="large"] .logo')
        .setAttribute('src', 'https://libapps.s3.amazonaws.com/sites/2210/banner/libguide-logo-fa17.png')
}

function main() {
    ccaCustomizations()
    // defined in broken-link-modal.js
    brokenLinkReports()
}

// run on a delay...#results load async not there when page loads
// TODO why is this necessary? is logo not present? BLR already loads on API success
setTimeout(main, 500)

})();
