# Changelog

## 2.6.0

**2021-02-23** - small improvements to Wagtail search, the Instagram app, and paging for the Exhibitions index. Add CCA Land Acknowledgement.

### Features

- [#123](https://github.com/cca/libraries_wagtail/issues/123) We have too many exhibits to simply show them all on the index; add paging so they're displayed 12 (3 rows of 4) at a time
- [#111](https://github.com/cca/libraries_wagtail/issues/111) add CCA Land Acknowledgement to the footer, copied verbatim from cca.edu
- Search improvements: [#115](https://github.com/cca/libraries_wagtail/issues/115) use "and" operator instead of "or", [#118](https://github.com/cca/libraries_wagtail/issues/118) focus on search text input when drawer is opened, [#110](https://github.com/cca/libraries_wagtail/issues/110) add `<title>` element to search results pages

### Bugfixes

- [#117](https://github.com/cca/libraries_wagtail/issues/117) download Instagram images to avoid relying on media links that expire
- [#124](https://github.com/cca/libraries_wagtail/issues/124) fix 500 error on certain requests to Hours API
- [0f9b4d1](https://github.com/cca/libraries_wagtail/commit/0f9b4d161d39a61d1ba2ac7979bf7d03a23d1e08) no download link for embedded art works in Exhibits
- Some changes to Brokenlinks app settings that make them work in more contexts
- A variety of minor (mostly npm) dependency updates

## 2.5.0

**2020-05-19** — implements Portal's "Image Grid" block, adds a Featured checkbox for Exhibits, and upgrades to Wagtail 2.9 while applying a host of smaller improvements.

### Features

- [#84](https://github.com/cca/libraries_wagtail/issues/84) Ability mark a "Featured Exhibit" that shows up on the home page beneath the latest news item
![example of Featured Exhibit](https://user-images.githubusercontent.com/1024833/81427010-eec9e580-910e-11ea-8fdb-3b13b631ad8d.png)
- [#89](https://github.com/cca/libraries_wagtail/issues/89) a clone of the "Image Grid" block from Portal with one small improvement: we can choose an internal page _or_ specify an external URL, instead of always needing an absolute URL even when linking to our own site.
![example Image Grid](https://user-images.githubusercontent.com/1024833/82011738-c66c4a80-962a-11ea-94e5-416c180c7b40.png)
- [Wagtail 2.9](https://docs.wagtail.io/en/stable/releases/2.9.html) comes with some security updates, bugfixes, caching of image renditions, and deprecates SiteMiddleware. We needed to change references to `{{ request.site.root_url }}` in our templates to use `{% wagtail_site as current_site %}{{ current_site.root_url }}` tag instead (occurs throughout our Schema.org metadata).
- [#101](https://github.com/cca/libraries_wagtail/issues/101) Sometimes we reference cool web projects and put URLs in our Instagram posts ([example](https://www.instagram.com/p/B_xfUb3h0Qw/)). Just because Instagram itself is a bad web citizen and doesn't link URLs in captions doesn't mean we can't.
- [#100](https://github.com/cca/libraries_wagtail/issues/100) 404 errors, mostly from robot crawlers, were absolutely flooding our django_error.log, making it contain super useful information buried in a sea of meaningless errors. I used logging filters to split these into a separate file.
- [#105](https://github.com/cca/libraries_wagtail/issues/105) Wagtail 2.8 had a sneaky useful feature in Reports, an admin feature that's good at listing pages which match certain criteria. I converted what used to be a management command into a "Pages lacking a Search Description" Report which makes it easier to identify pages not following our best practices.

### Bugfixes

- [#104](https://github.com/cca/libraries_wagtail/issues/104) While we have been logging document accesses in a CSV for a while, a Wagtail settings change accidentally caused most downloads to bypass logging. This version not only fixes that so all downloads are recorded but also makes the CSV formatting more foolproof by utilizing Python's `csv` library.

## 2.4.1

**2020-03-27** — Another somewhat rushed release, to get our Libraryh3lp chat presence on the website.

### Features

- [#96](https://github.com/cca/libraries_wagtail/issues/96) Libraryh3lp chat tab appears on every page when we're signed in

### Bugfixes

- [#97](https://github.com/cca/libraries_wagtail/issues/97) update Instagram APIs to use new Facebook graph ones, new way of obtaining OAuth access tokens and different data structure
- [#93](https://github.com/cca/libraries_wagtail/issues/93) fix a variety of accessibility issues identified by audits (link color contrast, search input label, aspect ratio of hamburger icon)

## 2.4.0

**2020-03-13** - Emergency update to highlight teaching & learning online resources. Update to Wagtail 2.8, update other dependencies.

### Features

- The **Services** box on the Libraries home page is highlighted in yellow. Rich text can be entered in the home page boxes now, allowing us to link to resources.
- **Wagtail 2.8** update, read [the release notes](https://docs.wagtail.io/en/v2.8/releases/2.8.html) for details. No significant changes.
- As part of the above, review & update Python dependencies (update to Django 2.2.11, django-cas-ng 4.1.1) and update the CCA Libraries version of the Internet Archive Bookreader.

### Bugfixes

- Convert all image blocks to linked image blocks, reduce number of blocks
- URLS longer than 200 characters break the Instagram app
- Validate hours API JSON parameters

## 2.3.0

**2019-11-07** - Update to Wagtail 2.7 with its improved editing interface, add Alerts app that syncs with major alerts published on Portal & displays them in a loud, red banner.

### Features

- **Wagtail 2.7**! Huge improvement for StreamField editor & a bunch of smaller niceties. Read [the release notes](https://docs.wagtail.io/en/v2.7/releases/2.7.html) for details.
- [#49](https://github.com/cca/libraries_wagtail/issues/49) Alerts app that lets us add our own alerts but also publishes ones from Portal (along with cca.edu). Code largely copied from cca.edu basis.
- [#87](https://github.com/cca/libraries_wagtail/issues/87) disable Book Review content type in Summon searches by default

### Bugfixes

- Ordered lists now display appropriately (they were displaying the same as unordered lists).
- Slight adjustment to main header height
- Uninstall Wand to disable animated GIF support. They posed a server stability problem.

### Misc

- Update a few `npm` packages & a bunch of `pip` requirements
- Searches are logged now
- [#88](https://github.com/cca/libraries_wagtail/issues/88) Convert to using `pipenv` for package/virtualenv management

## 2.2.1

**2019-09-06** - Enable the header search box in the Exhibits app. Also, the `search description` field (on the Promote panel of Wagtail admin) is now required for Exhibit pages.

## 2.2.0

**2019-08-28** — Portal-like "Card" blocks for main body content, sidebar resources, CAS login. A few design bug fixes.

### Features

- [#78](https://github.com/cca/libraries_wagtail/issues/78) New "Card" block with thumbnail image, linked title, and body text
- [#79](https://github.com/cca/libraries_wagtail/issues/79) Right-side (appears below main image, staff member) resource links and cards similar to above
- [#76](https://github.com/cca/libraries_wagtail/issues/76) CAS logins, no more need for a Wagtail-specific password
- Wagtail Document accesses are now tracked by a special CSV logger.

### Bugfixes

- Django security updates (v2.2.4)
- Update most python dependencies
- Fix some issues with mobile views on pages with fixed-width iframe embeds that overflow their wrapper's bounds and stretch the page. Semi-related, fix some `RowBlock` display issues with simpler flexbox code.

### Misc

- `RowBlock` layout defaults to equal-size columns instead of 60/40 left-biased. **NOTE:** this will change the behavior of existing rows without a "distribution" child block!
- Restructrure categories/models into a folder with multiple files
- New `LinkBlock` is useful when a link can be either internal/external but is lacking good validation (see [#80](https://github.com/cca/libraries_wagtail/issues/80))
- Enable Wagtail style guide on admin side

## 2.1.1

**2019-06-03** - several bugfixes, a few for problems introduced in the last release.

### Bugfixes

- [#77](https://github.com/cca/libraries_wagtail/issues/77) fix issues with Staff page mobile view
- [b049573](https://github.com/cca/libraries_wagtail/commit/b0495738b0777e3a82a89a0e53a9a8efd42bcb9f) `{% spaceless %}` filter proved problematic (can remove textual space between inline HTML tags like `<a>`, smushing them together). Also researched `django-htmlmin` but it a) doesn't work with GZip middleware & b) seems ill-maintained
- [c28b312](https://github.com/cca/libraries_wagtail/commit/c28b3120131d0d18ef1fe7fa2a8ac4d10177cb74) Instagram segment of home page could overflow boundaries if text contained very long words (e.g. URL or very long hashtag)
- Schema.org data could be malformed if text contained quotes or a script tag appeared early on in the page body
- Fix vulnerabilities identified by GitHub (fstream NPM package, Django rest framework)
- Update to Wagtail 2.5.1

## 2.1

**2019-05-17** — This version number is made up! But it's certainly not 1.0, we just haven't done changelogs until now.

### Features

- Update [Libraries Bookreader](https://github.com/cca/libraries_bookreader) to latest version from Internet Archive, 4.2.0
- [#57](https://github.com/cca/libraries_wagtail/issues/57) Add [Schema.org](https://schema.org/) linked data to most pages
- [#75](https://github.com/cca/libraries_wagtail/issues/75) Update to Wagtail 2.5
    + Adds new formatting options to richtext editor such as <sub>subscript</sub>, <sup>superscript</sup>, ~~strikethrough~~, and `code`

### Bugfixes

- [c0bd94e](https://github.com/cca/libraries_wagtail/commit/c0bd94e1f951e9d785d00e767fcca26c867345db) Staff page didn't underline "About Us" category link due to a typo
- [5d29cf8](https://github.com/cca/libraries_wagtail/commit/5d29cf8c0cb1d029f0dfc7d159cbcdee89b92675) iFrame embeds could expand beyond the page width on mobile

### Misc

- added `change_etadmin_owner` and `no_search_description` management commands
- `condense_whitespace` template tag to strip excess tabs, newlines, etc from text fields
- wrapped templates in `{% spaceless %}` to reduce HTML size
