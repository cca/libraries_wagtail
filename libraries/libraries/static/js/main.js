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
  var pageName = window.location.pathname.replace(/\//g,'');

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
  var $blogSidebarContent = $('.js-blog-sidebar-content');
  var $blogSidebarList = $('.js-blog-sidebar-list');
  var $footer = $('.js-footer');

  $blogSearchToggle.click(function(e) {
    e.preventDefault();
    $blogSidebarContent.slideToggle();
    $blogSearchToggle.toggleClass(
      'blog-articles-toggle--is-active'
    );
  });

  // -- Blog sidebar scroll (desktop only) -- \\

  var docHeight = document.body.scrollHeight;
  var viewHeight = document.documentElement.clientHeight;
  var maxHeight = docHeight - viewHeight;
  var footerHeight = $footer.height();
  var bodyWithoutfooterHeight = maxHeight - footerHeight;

  if ($blogSidebar.length > 0) {
    $window.on('scroll', function(e) {
      if ($window.width() > breakpoints.large) {
        var scrollPosition = $window.scrollTop();

        if (scrollPosition > bodyWithoutfooterHeight) {
          var offset = scrollPosition - bodyWithoutfooterHeight + 240;
          $blogSidebarList.css(
            'max-height',
            'calc(100vh - ' + offset + 'px)'
          );
        } else {
          $blogSidebarList.removeAttr('style');
        }
      }
    });
  }

  // -- Collections navigation scroll (desktop only) -- \\

  var $collectionsNav = $('.js-collections-nav');

  if ($collectionsNav.length > 0) {
    var $collectionItems = $('.js-collection-item');
    var $collectionsNavItems = $('.js-collections-nav-item');
    var collectionNavActiveCls = 'collections-nav-item--is-active';

    $window.on('scroll', function(e) {
      $collectionItems.each(function(i, item) {
        var visible = isInView(item);

        if (visible) {
          $collectionsNavItems.removeClass(collectionNavActiveCls);
          var $collectionsNavItemLink = $(
            ".js-collections-nav-item-link[href^='#" + item.id + "']"
          );
          $collectionsNavItemLink.parent().addClass(
            collectionNavActiveCls
          );
        }
      });
    });
  }

  // Check if element is in view
  // https://stackoverflow.com/a/42777210/5386237
  function isInView(el) {
    const { top, bottom } = el.getBoundingClientRect()
    return top >= 0 && bottom <= window.innerHeight
  }

  // -- Anchor link scrolling -- \\

  $("a.js-scroll-to[href^='#']").click(function(e) {
    e.preventDefault();
    var dest = $(this).attr('href');
    $('html, body').animate(
      { scrollTop: $(dest).offset().top - 100 }, // offset header
      'medium'
    );
    $window.trigger('scroll'); // needed for collection nav etc
  });
}

document.addEventListener('DOMContentLoaded', main);
