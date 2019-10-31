# Changelog

## 2.3.0

**DATE** - Add Alerts app that syncs with major alerts published on Portal & displays them in a loud, red banner.

### Features

- [#49](https://github.com/cca/libraries_wagtail/issues/49) Alerts app that lets us add our own alerts but also publishes ones from Portal (along with cca.edu). Code largely copied from cca.edu basis.
- [#87](https://github.com/cca/libraries_wagtail/issues/87) disable Book Review content type in Summon searches by default

### Bugfixes

- Ordered lists now display appropriately (they were displaying the same as unordered lists).
- Slight adjustment to main header height
- Uninstall Wand to disable animated GIF support. This is posing a server stability problem.

### Misc

- Update a few `npm` packages & a bunch of `pip` requirements
- Searches are logged now

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
