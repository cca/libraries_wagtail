# Changelog

## 5.0.0

**2024-01-30**: upgrade to Wagtail 5.0, fix Instagram (again), accessibility improvements on the home page.

- Many [new features from Wagtail 5.0](https://guide.wagtail.org/en-latest/releases/new-in-wagtail-5-0/):
  - See how many times an image is used before deleting it
  - SVG image uploads
  - Always-on minimap in editor
  - Dark mode admin theme
- Refactor our CSS to fix SASS deprecations (`@use` and namespaced variables)
- New process for adding Instagram post to home page
- Many accessibility improvements
  - Wagtail accessibility checker improvements
  - Use Instagram's accessibility caption as alt text. It is machine-generated when we do not provide one (but we should be providing these!)
  - Many home page improvements: remove redundant link titles, add h1 tag, fieldset for search radio buttons
- Better error messages for Link Blocks
- Remove Summon custom JS/CSS; this is added to the Summon admin console now
- Upgrade Django and many other dependencies
- Local development fixes and improvements

## 4.2.0

**2024-08-23**: upgrade to Wagtail 4.2 and change the main building address.

- Change the building address to 145 Hooper in the footer and schema.org metadata
- New [Accessibility Checker](https://docs.wagtail.org/en/stable/releases/4.2.html#accessibility-checker-integration) when you are signed in as an editor
- Fix an accessibility issue highlighted by the checker! The header hierarchy in the site footer
- [Rich text editor improvements](https://docs.wagtail.org/en/stable/releases/4.2.html#rich-text-improvements), you can choose between an inline floating toolbar or a fixed one
- Sort the "Pages lacking a Search Description" report by date last published
- Minor upgrades to non-Wagtail/Django dependencies
- Add [eslint](https://eslint.org/) to aid consistent JavaScript style
- Reformat many SCSS (due to the [mixed declarations](https://sass-lang.com/documentation/breaking-changes/mixed-decls/) deprecation) and JS files (thanks to `eslint`)
- Local development CAS server URL changed
- Documentation updates

## 4.1.1

**2024-02-26**: upgrade to Wagtail 4.1 which has even more new page editing features!

- Wagtail 4.0 included a [page editor resedign](https://docs.wagtail.org/en/stable/releases/4.0.html#page-editor-redesign)
- "Minimap" of the page in a right-hand panel that expands on hover. This seems sort of buggy, it will collapse before you can click on anything unless you keep your cursor to the far right
- "Collapse all" / "Expand all" buttons in the upper right for sections of the page
- A series of [rich text improvements](https://docs.wagtail.org/en/stable/releases/4.0.html#rich-text-improvements)
  - Type forward slash `/` to bring up a list of available formats (lists, heading) and our blocks (linked image, card, etc). You can insert a block in the middle of a Paragraph to split it in two, which replaces the scissors icon from the last release
- Live preview panel—see changes in real time
- You can sort [images](https://libraries.cca.edu/admin/images/) by different fields
- "What's New" section on the admin dashboard and a new Help menu
- Images and snippets now report how many times they're "used" (included in pages)

## 4.1.0

**2024-02-22**: upgrade to Wagtail 3.0 which features a big overhaul of the editorial UI. More software updates.

- The editorial UI looks very different, see the [Wagtail 3.0 release notes](https://docs.wagtail.org/en/stable/releases/3.0.html#page-editor-redesign) for specific details.
- Scissors icon lets you split a Paragraph block in two
- Paragraphs support embedded content (e.g. YouTube videos) though it displays very small
- Our pages types have brief descriptions in the admin UI
- Duplicate image upload detection (I haven't gotten this to work in my testing, though)
- More dependency upgrades (whitenoise, uWSGI, Django, django-storages, djangorestframework-simplejwt, django-cas-ng)

## 4.0.0

**2024-02-16**: a huge number of critical software updates. If nothing seems different after this upgrade, that's a good thing! These upgrades position us to upgrade Wagtail itself which will bring new features.

- [#52](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/52) anchor links now account for the fixed header
- [#33](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/33) fixed a long-running challenge of serving media files when developing locally
- a large number of dependency updates, switch from deprecated [node-sass](https://www.npmjs.com/package/node-sass) to [dart-sass](https://www.npmjs.com/package/sass)
- upgrade the site's PostgresQL database from 9.6 to 14.7 (for production, staging is 14.9)
- [#54](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/54) upgrade the site's search engine (Elasticsearch) from 5 to 7
- [#55](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/55) upgrade python from 3.7 to 3.10
- [#10](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/10) hide `SECRET_KEY` from the code base
- use Google Secret Manager for some app secrets (Elasticsearch, email, and Instagram credentials)
- improve CI/CD pipeline (skip unneeded step for staging, use cache when building Docker images) and switch to Artifact Registry

## 3.3.0

**2023-04-27** - two major Wagtail upgrades. Add Promoted Search Results plugin. Fix a bug with navigating between blog posts on a phone-sized screen.

- [Wagtail 2.15 upgrade](https://docs.wagtail.org/en/latest/releases/2.15.html) brings bulk actions for pages, documents, images (e.g. tag multiple images at once). The title field on Image and Document uploads now defaults to the filename without the file extension.
- [Wagtail 2.16 upgrade](https://docs.wagtail.org/en/latest/releases/2.16.html) brings a new "slim" admin sidebar, automatic redirect creation, ["aging pages" report](https://libraries.cca.edu/admin/reports/aging-pages/).
- Google site verification for [Search Console](https://search.google.com/search-console/about)
- Switch back to using Wagtail's document serving method; the issue of PDFs forcing downloads instead of being readable in the browser appears to have been resolved
- [Promoted Search Results](https://guide.wagtail.org/en-latest/how-to-guides/promote-search-results/) is a Wagtail plugin which adds a Settings page where we can force certain pages to appear at the top of certain searches, e.g. the Inter-library Loan page for "ILL" (when it would not normally appear)
- [#45](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/45) fix Summon CSS file 404s, also makes docker build process more streamlined
- [#48](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/48) use kubernetes secrets for Summon SFTP details as opposed to `docker cp` (security improvement)
- [#49](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/49) fix blog post pagination on mobile

## 3.2.1

**2023-01-19** - allow scheduling posts ahead of time. Many updates to backend tools, remove a couple instances of outdated info.

- [#38](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/38) add `publish_scheduled_pages` cron job
- Upgrade Skaffold development tool to 2.0
- Migrate from Universal Analytics to Google Analytics 4
- Kubernetes updates related to v1.22
- Migrate to using private key authentication with the Summon FTP service
- Remove defunct Twitter link in footer
- [#39](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/39) Remove Meyer from home page hours box

## 3.2.0

**2022-09-20** - buttons on the home page, increased font size, and performance improvements. Many behind-the-scenes updates to dependencies that have no obvious impact but are nonetheless necessary maintenance.

- [#26](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/26) button styles for links in the home page info boxes.
- [#36](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/36) pull thumbnails automatically for Panopto videos in Exhibitions.
- [#27](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/27), [#34](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/34), [#35](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/35) major performance improvements, especially for Exhibitions: long-term caching headers for static assets, preconnect for the GSB domain, lazy loading exhibit images.
- [#37](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/37) larger main body font sizes
- References to Meyer Library that were hard-coded in a few places (the footer, the Hours page, the preview of our hours on the About Us page) were removed.
- [Wagtail 2.14](https://docs.wagtail.org/en/latest/releases/2.14.html) upgrade which brings no major new features.
- _Many_ dependency updates, mostly to non-Wagtail software, including Django, Psycopg2, uWSGI, whitenoise, and our various Django addons (CAS, storage, extensions).

## 3.1.0

**2022-06-30** - create a workflow to run the site locally in a local kubernetes cluster that resembles our staging and production deployments. Perform four Wagtail core updates. Performance improvements in the site header and on the home page. Previews should more reliably show changes as opposed to cached, outdated versions of a page.

### Features

- New development tools under the "docs" directory. The setup.sh script bootstraps a development environment, the sync.fish script synchronizes the local database and media with the remote instances, and the dev.fish script starts/stops the local development toolchain.
- [Wagtail 2.10](https://docs.wagtail.org/en/stable/releases/2.10.html) upgrade: [Moderation Workflows](https://docs.wagtail.org/en/stable/editor_manual/administrator_tasks/managing_workflows.html#managing-workflows) are improved, we use the [Legacy richtext](https://docs.wagtail.org/en/stable/reference/contrib/legacy_richtext.html) middleware to simplify some styles, and there are new workflow and "site history" reports.
- [Wagtail 2.11](https://docs.wagtail.org/en/stable/releases/2.11.html) upgrade: adds locale field to page model to support [multi-language content](https://docs.wagtail.org/en/stable/advanced_topics/i18n.html#multi-language-content), [page aliases](https://docs.wagtail.org/en/stable/releases/2.11.html#page-aliases), and [nested media collections](https://docs.wagtail.org/en/stable/releases/2.11.html#collections-hierarchy).
- [Wagtail 2.12](https://docs.wagtail.org/en/stable/releases/2.12.html) upgrade: [customizing admin UI colors](https://docs.wagtail.org/en/stable/advanced_topics/customisation/admin_templates.html#custom-user-interface-colors), update the convert_images_blocks.py script.
- [Wagtail 2.13](https://docs.wagtail.org/en/stable/releases/2.13.html) upgrade: duplicate blocks while editing pages, internal [commenting](https://docs.wagtail.org/en/stable/editor_manual/editing_existing_pages.html#commenting) is available but not added to any of our page models yet.

We're not using many of the new features in these Wagtail versions but the upgrades are part of an effort to bring us up to date so when features we _do_ want to use are introduced, we're able to acquire them quickly.

### Bugfixes

- The **Summon Deletes** script temporarily stopped working due to a pair of problems (a change to Summon's FTP server and one to Koha's date formatting).
- Minor accessibility improvements (e.g. better color contrast for the links on the home page "info boxes")

## 3.0.0

**2021-10-27** - migrate the build/deploy/hosting to using Docker/GitLab CI/Google Cloud Platform and kubernetes. Add a command to update our deleted bibliographic records in Summon and require a search description for almost all pages.

### Features

- Entirely new build and deploy process that promises quicker releases and more consistency between development and production versions. As a consequence, the app has moved from [GitHub](https://github.com/cca/libraries_wagtail) to a private [GitLab](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu) repo.
- Images, videos, and documents are now saved to and served from a Google Storage Bucket. All their URLs have changed and must be updated in external sources such as Koha (which used the app to host material type icons).
- **Summon Deletes**: a new management command runs a Koha report and then SFTPs the results to Summon to update our discovery index.
- More page types (`AboutUs`, `Service`, `Category`, `SpecialCollection`, and `Blog`) require a search description field under the **Promote** tab. Also, `RowComponent` pages are excluded from the search description report since they do not appear in search results.

### Outstanding Bugs

- GL [#7](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/7) Cron jobs are not working yet so Instagram & Summon commands must be run manually
- We may need to create a new Instagram app on Facebook's developers platform if the client_id and secret of the previously-existing app on production cannot be located
- GL [#14](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/14) the flip bookreader app is no longer deployed at https://libraries.cca.edu/static/bookreader/ but it also server no purpose currently as VAULT is still down from the October 1st server outage
- GL [#3](https://gitlab.com/california-college-of-the-arts/libraries.cca.edu/-/issues/3) logs are no longer persistent, they're wiped out by each release

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
