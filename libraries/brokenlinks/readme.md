# Summon (or other discovery layer) Broken Links app

This app receives POSTed information and sends it to a Google Spreadsheet for analysis. It records the OpenURL, Summon permalink, and Summon content type of the item with the broken link as well as an email and open-ended comments field from the user reporting the broken link. To configure this app:

1. create a Google Form with fields for each of the data listed above
2. make sure it can be submitted by _anyone_ not just your particular institution
3. view the form and copy its URL, changing the last path component to "formResponse" e.g. `https://docs.google.com/forms/d/e/{{key}}/formResponse`
4. put the URL into a settings file (e.g. libraries/settings/local.py) with name `BROKENLINKS_GOOGLE_SHEET_URL`
5. find the ID values of each input, like "entry.123123123", easiest way to do this is to create a prefilled link then look at the URL for where it's filling in your values
6. enter those into the `BROKENLINKS_HASH` setting
7. insert the included JavaScript into Summon, double-checking the URLs

The "cca-broken-link-modal.js" JavaScript is not actually used anywhere in Wagtail; it's included merely for reference, but should be added to a customized script for Summon.
