function main() {
  // These need to match with the breakpoints
  // written in scss/settings/_breakpoints.scss
  let breakpoints = {
    small: 460,
    medium: 640,
    large: 1000,
  }

  let $page = $('.js-page')

  // -- Header search toggle -- \\
  let $header = $('.js-header')
  let $headerSearchIcon = $('.js-header-search')
  let $headerSearchBox = $('.js-header-search-box')
  let headerSearchInput = document.querySelector('.js-search-input')
  let headerLinkActiveCls = 'header__nav-link--is-active'
  let pageOverlayCls = 'page--overlay'

  // Toggle elements
  function toggleSearch(state) {
    $headerSearchIcon.toggleClass(headerLinkActiveCls, state)
    $headerSearchBox.toggleClass('header-search-box--is-active', state)
    if (isInView(headerSearchInput)) headerSearchInput.focus()
  }

  $headerSearchIcon.click(function(e) {
    e.preventDefault()
    toggleNavigation(false) // hide nav
    toggleSearch()
    $page.toggleClass(
      pageOverlayCls,
      $headerSearchIcon.hasClass(headerLinkActiveCls)
    )
  })

  // -- Header navigation toggle -- \\
  let $headerHamburgerIcon = $('.js-header-hamburger')
  let $headerNavigation = $('.js-main-navigation')

  // Toggle elements
  function toggleNavigation(state) {
    $headerHamburgerIcon.toggleClass(headerLinkActiveCls, state)
    $headerNavigation.toggleClass('main-navigation--is-active', state)
  }

  // Non-anon function becuase we use it separately
  function hamburgerClickHandler(e) {
    e ? e.preventDefault() : null // jshint ignore:line

    // on the search page we need toggle the search box
    isSearchPage ? toggleSearch() : toggleSearch(false) // jshint ignore:line
    toggleNavigation();
    $page.toggleClass(
      pageOverlayCls,
      $headerHamburgerIcon.hasClass(
        headerLinkActiveCls
      )
    )
  }

  $headerHamburgerIcon.click(hamburgerClickHandler)

  // -- Page overlay toggle -- \\

  // Hide everything if page overlay is clicked
  $(document).on('click', '.' + pageOverlayCls, function(e) {
    e.preventDefault()
    if ($(e.target).hasClass(pageOverlayCls)) {
      toggleSearch(false)
      toggleNavigation(false)
      $page.toggleClass(pageOverlayCls, false)
    }
  })

  // This is needed to stop the clicks from the nav
  // links and search-box falling through to the page
  // overlay click handler (above).
  $header.click(e => { e.stopPropagation() })

  // -- Page helper class -- \\

  // Add a class of the page name for help with main navigation.
  let pageName = window.location.pathname.replace(/\//g,'')

  // Search pages can contain query params so the pageName isn't pure
  let isSearchPage = pageName.indexOf('search') > -1

  // The home page uri is `/` so pageName is
  // an empty string
  if (pageName.length > 0) {
    isSearchPage ? $page.addClass('page--search') : $page.addClass('page--' + pageName) // jshint ignore:line
  } else {
    $page.addClass('page--home')
  }

  // -- Search page search box display -- \\

  // If we're on the search page, open the search box
  // and disable the button so it can't be hidden;
  if (pageName.indexOf('search') > -1) {
    toggleSearch(true)
    $headerSearchIcon.off('click')
    $headerSearchIcon.click(function(e) {
      e.preventDefault()

      // If the link nav is open, hide it
      if ($headerHamburgerIcon.hasClass(headerLinkActiveCls)) {
        hamburgerClickHandler()
      }
    })
  }

  // -- Responsive helpers -- \\

  // We want to debounce the resize event so we're
  // not running these functions a billion times.
  let resizeTimer,
      $window = $(window);

  // Get the browser width on change
  $window.on('resize', function(e) {
    clearTimeout(resizeTimer)
    resizeTimer = setTimeout(function() {
      let browserWidth = $window.width()

      // Reset the nav if going from small to big
      if (browserWidth > breakpoints.medium) {
        if ($headerHamburgerIcon.hasClass(headerLinkActiveCls)) {
          hamburgerClickHandler()
        }
      }
    }, 250)
  })

  // -- Blog sidebar toggle (mobile only) -- \\

  let $blogSearchToggle = $('.js-blog-search-toggle')
  let $blogSidebar = $('.js-blog-sidebar')
  let $blogSidebarContent = $('.js-blog-sidebar-content')
  let $blogSidebarList = $('.js-blog-sidebar-list')
  let $footer = $('.js-footer')

  $blogSearchToggle.click(function(e) {
    e.preventDefault()
    $blogSidebarContent.slideToggle()
    $blogSearchToggle.toggleClass('blog-articles-toggle--is-active')
  })

  // -- Collections navigation scroll (desktop only) -- \\

  let $collectionsNav = $('.js-collections-nav')

  if ($collectionsNav.length > 0) {
    let $collectionItems = $('.js-collection-item')
    let $collectionsNavItems = $('.js-collections-nav-item')
    let $collectionsTitle = $('.js-collections-title')
    let collectionNavActiveCls = 'collections-nav-item--is-active'

    $window.on('scroll', function(e) {
      $collectionItems.each(function(i, item) {
        let visible = isInView(item)
        let id = $(item).find('a.anchor').attr('id')

        if (visible) {
          $collectionsNavItems.removeClass(collectionNavActiveCls);
          $(`.js-collections-nav-item-link[href^='#${id}']`)
            .parent().addClass(collectionNavActiveCls);
        }

        if (isInView($collectionsTitle[0])) {
            $collectionsNav.css('top', '').css('bottom', '')
        // if the footer's even partially in view, don't let menu overlap it
        } else if (isInView($footer[0], true)) {
            $collectionsNav.css('top', '')
            $collectionsNav.css('bottom', $footer.outerHeight(true) + 'px')
        } else {
            // if we're below the header, pull the nav menu up a bit
            $collectionsNav.css('top', $header.outerHeight(true) + 'px')
            $collectionsNav.css('bottom', '')
        }

      })
    })
  }

  // Check if element is in view
  // https://stackoverflow.com/a/42777210/5386237
  function isInView(el, partial) {
      // can't do const { top, bottom } bc uglify chokes on it -EP
      let rect = el.getBoundingClientRect()
          , top = rect.top
          , bottom = rect.bottom;
      if (partial) {
          return top < window.innerHeight && bottom >= 0
      }

      return top >= 0 && bottom <= window.innerHeight
  }

  // -- Anchor link scrolling -- \\

  $("a.js-scroll-to[href^='#']").click(function(e) {
    e.preventDefault();
    let dest = $(this).attr('href');
    $('html, body').animate(
      { scrollTop: $(dest).offset().top - 100 }, // offset header
      'medium'
    );
    $window.trigger('scroll'); // needed for collection nav etc
  });
}

document.addEventListener('DOMContentLoaded', main);
