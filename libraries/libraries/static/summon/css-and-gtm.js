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

function addGTM() {
    // https://github.com/tabathafarney/GoogleTagManager-Summon/blob/master/add-gtm-summon.js
    // this GTM instance triggers Summon's GA4 property
    $("body").prepend("<script>var vPagePath = window.location.href;dataLayer = [{'virtualURL': vPagePath}];</script><noscript><iframe src='//www.googletagmanager.com/ns.html?id=GTM-TKFJGG7' height='0' width='0' style='display:none;visibility:hidden'></iframe></noscript><script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='//www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-TKFJGG7');</script>");
}

function main() {
    ccaCustomizations()
    addGTM()
    // defined in broken-link-modal.js
    brokenLinkReports()
}

// run on a delay...#results load async not there when page loads
setTimeout(main, 500)

})();
