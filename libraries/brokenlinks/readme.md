# Summon (or other discovery layer) Broken Links app

This app receives POSTed information and sends it to a Google Spreadsheet for analysis. It records the remote IP address, OpenURL data, Summon permalink, and Summon content type of the item with the broken link as well as an email and open-ended comments field from the user reporting the broken link. To configure this app:

1. create a Google Form with fields for each of the data listed above
2. make sure it can be submitted by _anyone_ not just your particular institution
3. view the form and copy its key, `https://docs.google.com/forms/d/e/{{key}}/viewform`
4. put the key into a settings file (e.g. libraries/settings/local.py) with name BROKENLINKS_GOOGLE_SHEET_KEY
5. inspect all the HTML `<input>` elements, finding their `name` attributes with values like "entry.123123123"
6. enter those into the BROKENLINKS_HASH setting
7. insert the included JavaScript into Summon, double-checking the URLs

The JavaScript is not actually used anywhere in Wagtail; it's included merely for convenience, but should be added to a customized script for Summon.
