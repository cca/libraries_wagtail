# Changelog

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
