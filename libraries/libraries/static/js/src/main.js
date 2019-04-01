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

  // -- Collections navigation scroll (desktop only) -- \\

  var $collectionsNav = $('.js-collections-nav');

  if ($collectionsNav.length > 0) {
    var $collectionItems = $('.js-collection-item');
    var $collectionsNavItems = $('.js-collections-nav-item');
    var $collectionsTitle = $('.js-collections-title')
    var collectionNavActiveCls = 'collections-nav-item--is-active';

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

      });
    });
  }

  // Check if element is in view
  // https://stackoverflow.com/a/42777210/5386237
  function isInView(el, partial) {
      // can't do const { top, bottom } bc uglify chokes on it -EP
      var rect = el.getBoundingClientRect()
          , top = rect.top
          , bottom = rect.bottom;
      if (partial) {
          return top < window.innerHeight && bottom >= 0
      } else {
          return top >= 0 && bottom <= window.innerHeight
      }
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

/*! @preserve
 * Fairy Dust Cursor.js
 * - 90's cursors collection
 * -- https://github.com/tholman/90s-cursor-effects
 * -- http://codepen.io/tholman/full/jWmZxZ/
 */

(function fairyDustCursor() {

  var possibleColors = ["#D61C59", "#E7D84B", "#1B8798"]
  var width = window.innerWidth;
  var height = window.innerHeight;
  var cursor = {x: width/2, y: width/2};
  var particles = [];

  function init() {
    bindEvents();
    loop();
  }

  // Bind events that are needed
  function bindEvents() {
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('touchmove', onTouchMove);
    document.addEventListener('touchstart', onTouchMove);

    window.addEventListener('resize', onWindowResize);
  }

  function onWindowResize(e) {
    width = window.innerWidth;
    height = window.innerHeight;
  }

  function onTouchMove(e) {
    if( e.touches.length > 0 ) {
      for( var i = 0; i < e.touches.length; i++ ) {
        addParticle( e.touches[i].clientX, e.touches[i].clientY, possibleColors[Math.floor(Math.random()*possibleColors.length)]);
      }
    }
  }

  function onMouseMove(e) {
    cursor.x = e.clientX;
    cursor.y = e.clientY;

    addParticle( cursor.x, cursor.y, possibleColors[Math.floor(Math.random()*possibleColors.length)]);
  }

  function addParticle(x, y, color) {
    var particle = new Particle();
    particle.init(x, y, color);
    particles.push(particle);
  }

  function updateParticles() {

    // Updated
    for( var i = 0; i < particles.length; i++ ) {
      particles[i].update();
    }

    // Remove dead particles
    for( var i = particles.length -1; i >= 0; i-- ) {
      if( particles[i].lifeSpan < 0 ) {
        particles[i].die();
        particles.splice(i, 1);
      }
    }

  }

  function loop() {
    requestAnimationFrame(loop);
    updateParticles();
  }

  /**
   * Particles
   */

  function Particle() {

    this.character = "*";
    this.lifeSpan = 120; //ms
    this.initialStyles ={
      "position": "fixed",
      "top": 0,
      "display": "block",
      "pointerEvents": "none",
      "z-index": "10000000",
      "fontSize": "24px",
      "will-change": "transform"
    };

    // Init, and set properties
    this.init = function(x, y, color) {

      this.velocity = {
        x:  (Math.random() < 0.5 ? -1 : 1) * (Math.random() / 2),
        y: 1
      };

      this.position = {x: x - 10, y: y - 20};
      this.initialStyles.color = color;

      this.element = document.createElement('span');
      this.element.innerHTML = this.character;
      applyProperties(this.element, this.initialStyles);
      this.update();

      // append to main wrapper & not body
      document.querySelector('main').appendChild(this.element);
    };

    this.update = function() {
      this.position.x += this.velocity.x;
      this.position.y += this.velocity.y;
      this.lifeSpan--;

      this.element.style.transform = "translate3d(" + this.position.x + "px," + this.position.y + "px,0) scale(" + (this.lifeSpan / 120) + ")";
    }

    this.die = function() {
      this.element.parentNode.removeChild(this.element);
    }

  }

  /**
   * Utils
   */

  // Applies css `properties` to an element.
  function applyProperties( target, properties ) {
    for( var key in properties ) {
      target.style[ key ] = properties[ key ];
    }
  }

  init();
})();
