# Summon Deletes

When a record is deleted from our local catalog (Koha), we must update the Summon discovery layer index or else the item will continue to appear in search results. We had done this semi-manually previously with code in the [cca/libraries_branding](https://github.com/cca/libraries_branding/tree/main/summon) project. By converting those scripts to Python and storing information about previous runs, we can make this task into an automated procedure run by cron.

## Custom JavaScript

Summon lets you load a custom JavaScript file under the setting "[Summon 2.0 External Script](https://customize.summon.serialssolutions.com/settings#Summon20ExternalScript)". Our JS does a few things:

- provide our "broken link" reporting (mostly copied from Fairfield U's code)
- insert a custom CSS file (which Summon doesn't provide an option for)
- initialize Google Tag Manager (we are using Tabatha Farney's [GTM configuration for Summon](https://github.com/tabathafarney/GoogleTagManager-Summon))

We previously stored this code in the [libraries_branding](https://github.com/cca/libraries_branding/tree/main/summon) GitHub project which compiled and synced the code to our static files folder on the Wagtail server. This approach stopped working when we transitioned to using whitenoise for static files and kubernetes.

## Setup

This task depends on `pysftp` and is the sole reason for that dependency. There is a `SummonDelete` model under this app that represents previous runs of the task; a `SummonDelete` includes the date of the run, the number of deleted records, and a text list of deleted records. We hook this app up to a public Koha JSON report which simply returns the identifiers (biblionumbers) of deleted records and nothing else. Set this to `SUMMON_REPORT_URL`.

The `SUMMON_SFTP_URL` is also set in our base settings while `SUMMON_SFTP_UN` and `SUMMON_SFTP_PW` are secret and must be configured in your local settings.

By default, pysftp checks ~/.ssh/known_hosts (/root/.ssh/known_hosts on a kubernetes pod) and it will not connect to a server if it is not listed there. To work around this, we include our own known_hosts file in the management/commands directory. In the past, the command has stopped working when Summon changed the address of their FTP server. We can update known_hosts by running a shell on a pod, connecting to Summon's FTP with `sftp cca-catalog@ftp.summon.serialssolutions.com`, typing "yes" at the prompt, and copying the updated /root/.ssh/known_hosts file.

The first time the task runs, there are no previous iterations, which can cause an error. The management command accepts a "date last run" argument so you can run `python manage.py summon_deletes "YYYY/MM/DD"` the first time.

After the initial run, the task can be added as a cron job and run regularly.
