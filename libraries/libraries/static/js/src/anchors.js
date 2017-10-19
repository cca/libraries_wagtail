let anchorScroll = () => {
    if (location.hash != '') {
        // if we don't do this tiny delay, scroll doesn't happen ¯\_(ツ)_/¯
        setTimeout(() => {
            window.scrollBy(0, -1 * document.querySelector('header').offsetHeight)
        }, 100)
    }
}
// run on document load
if (document.readyState === "complete") {
    anchorScroll()
} else {
    document.addEventListener("DOMContentLoaded", anchorScroll)
}
