# Summon Deletes

When a record is deleted from our local catalog (Koha), we must update the Summon discovery layer index or else the item will continue to appear in search results. We had done this semi-manually previously with code in the [cca/libraries_branding](https://github.com/cca/libraries_branding/tree/main/summon) project. By converting those scripts to Python and storing information about previous runs, we can make this task into an automated procedure run by cron.

## Setup

This task depends on `pysftp` and is the sole reason for that dependency. There is a `SummonDelete` model under this app that represents previous runs of the task; a `SummonDelete` includes the date of the run, the number of deleted records, and a text list of deleted records. We hook this app up to a public Koha JSON report which simply returns the identifiers (biblionumbers) of deleted records and nothing else. Set this to `SUMMON_REPORT_URL`.

The `SUMMON_SFTP_URL` is also set in our base settings while `SUMMON_SFTP_UN` and `SUMMON_SFTP_PW` are secret and must be configured in your local settings.

By default, pysftp checks ~/.ssh/known_hosts and it will not connect to a server if it is not listed there. So I recommend manually connecting to the Summon SFTP server like `sftp $SUMMON_SFTP_UN@$SUMMON_SFTP_URL`, filling in the appropriate values and inserting our password at the prompt, which will prompt you to add the host to known_hosts.

The first time the task runs, there are no previous iterations, which can cause an error. The management command accepts a "date last run" argument so you can run `python manage.py summon_deletes "YYYY/MM/DD"` the first time.

After the initial run, the task can be added as a cron job and run regularly.
