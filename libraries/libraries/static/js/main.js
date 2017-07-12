'use strict';

function main() {

  // These need to match with the breakpoints
  // written in scss/settings/_breakpoints.scss
  var breakpoints = {
    small: 460,
    medium: 640,
    large: 1000,
  };

  var $page = $('.js-page');

  // -- Header search toggle -- \\

  var $header = $('.js-header');
  var $headerSearchIcon = $('.js-header-search');
  var $headerSearchBox = $('.js-header-search-box');
  var headerLinkActiveCls = 'header__nav-link--is-active';
  var pageOverlayCls = 'page--overlay';

  // Toggle elements
  function toggleSearch(state) {
    $headerSearchIcon.toggleClass(
      headerLinkActiveCls,
      state
    );
    $headerSearchBox.toggleClass(
      'header-search-box--is-active',
      state
    );
  }

  $headerSearchIcon.click(function(e) {
    e.preventDefault();
    toggleNavigation(false); // hide nav
    toggleSearch();
    $page.toggleClass(
      pageOverlayCls,
      $headerSearchIcon.hasClass(
        headerLinkActiveCls
      )
    );
  });

  // -- Header navigation toggle -- \\

  var $headerHamburgerIcon = $('.js-header-hamburger');
  var $headerNavigation = $('.js-main-navigation');

  // Toggle elements
  function toggleNavigation(state) {
    $headerHamburgerIcon.toggleClass(
      headerLinkActiveCls,
      state
    );
    $headerNavigation.toggleClass(
      'main-navigation--is-active',
      state
    );
  }

  // Non-anon function becuase we use it seperatly
  function hamburgerClickHandler(e) {
    e ? e.preventDefault() : null;

    // on the search page we need toggle the search box
    isSearchPage ? toggleSearch() : toggleSearch(false);
    toggleNavigation();
    $page.toggleClass(
      pageOverlayCls,
      $headerHamburgerIcon.hasClass(
        headerLinkActiveCls
      )
    );
  }

  $headerHamburgerIcon.click(hamburgerClickHandler);

  // -- Page overlay toggle -- \\

  // Hide everything if page overlay is clicked
  $(document).on('click', '.' + pageOverlayCls, function(e) {
    e.preventDefault();
    if ($(e.target).hasClass(pageOverlayCls)) {
      toggleSearch(false);
      toggleNavigation(false);
      $page.toggleClass(pageOverlayCls, false);
    }
  });

  // This is needed to stop the clicks from the nav
  // links and search-box falling through to the page
  // overlay click handler (above).
  $header.click(function(e) {
    e.stopPropagation();
  });

  // -- Page helper class -- \\

  // Add a class of the page name for help with
  // main navigation. We do this because of the
  // simplicity of mustache templages.
  var pageName = window.location.href.replace(/\//g, '');

  // Search pages can contain query params
  // so the pageName isn't pure
  var isSearchPage = pageName.indexOf('search') > -1;

  // The home page uri is `/` so pageName is
  // an empty string
  if (pageName.length > 0) {
    isSearchPage ?
      $page.addClass('page--search') :
      $page.addClass('page--' + pageName);
  } else {
    $page.addClass('page--home');
  }

  // -- Search page search box display -- \\

  // If we're on the search page, open the search box
  // and disable the button so it can't be hidden;
  if (pageName.indexOf('search') > -1) {
    toggleSearch(true);
    $headerSearchIcon.off('click');
    $headerSearchIcon.click(function(e) {
      e.preventDefault();

      // If the link nav is open, hide it
      if ($headerHamburgerIcon.hasClass(headerLinkActiveCls)) {
        hamburgerClickHandler();
      }
    });
  }

  // -- Responsive helpers -- \\

  // We want to debounce the resize event so we're
  // not running these functions a billion times.
  var resizeTimer,
      $window = $(window);

  // Get the browser width on change
  $window.on('resize', function(e) {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
      var browserWidth = $window.width();

      // Reset the nav if going from small to big
      if (browserWidth > breakpoints.medium) {
        if ($headerHamburgerIcon.hasClass(headerLinkActiveCls)) {
          hamburgerClickHandler();
        }
      }
    }, 250);
  });

  // -- Blog sidebar toggle (mobile only) -- \\

  var $blogSearchToggle = $('.js-blog-search-toggle');
  var $blogSidebar = $('.js-blog-sidebar');

  $blogSearchToggle.click(function(e) {
    e.preventDefault();
    $blogSidebar.slideToggle();
    $blogSearchToggle.toggleClass(
      'blog-articles-toggle--is-active'
    );
  });
}

document.addEventListener('DOMContentLoaded', main);
