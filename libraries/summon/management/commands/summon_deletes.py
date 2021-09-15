from datetime import date
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

import pysftp
import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from summon.models import SummonDelete

logger = logging.getLogger('mgmt_cmd.script')


class Command(BaseCommand):
    help = "Send a list of deleted bib records to the Summon SFTP server so they can be removed from our discovery index. This command is meant to be run on a schedule."

    def add_arguments(self, parser):
        parser.add_argument('lastrun', nargs='?', type=str,
                            help='date of last run (in YYYY/MM/DD format)')

    def handle(self, *args, **options):
        if not hasattr(settings, 'SUMMON_SFTP_UN') or not hasattr(settings, 'SUMMON_SFTP_PW'):
            raise CommandError("Requires a SUMMON_SFTP_UN and SUMMON_SFTP_PW configured in yout local.py settings.")
        # lastrun is a STRING (not date!) of form "YYYY/MM/DD"
        try:
            lastrun = options.get('lastrun', None) or SummonDelete.objects.latest('date').date.strftime('%Y/%m/%d')
        except SummonDelete.DoesNotExist:
            # on the first run the above will raise an error because there are
            # no SummonDelete.objects yet
            logger.error('There are no existing SummonDelete objects. Please run this management script with a "--lastrun YYYY/MM/DD" argument.')
            exit(1)
        logger.info("Summon deletes task was last run on {}".format(lastrun))

        response = requests.get(settings.SUMMON_REPORT_URL.format(quote(lastrun)))
        # Koha JSON is an array of arrays for each row of the report e.g. [[1], [2]]
        rows = response.json()
        number = len(rows)
        # unpack the record sub-lists into a newline-delimited string
        records = '\n'.join([str(rec) for [rec] in rows])
        logger.info("{} records were deleted since {}".format(number, lastrun))

        # write to file in temporary directory
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cca-catalog-deletes-{}.mrc".format(lastrun.replace('/', '-'))
            with path.open('w+') as fh:
                fh.write(records)
                fh.seek(0)
                # PUT file to Summon SFTP server
                with pysftp.Connection(settings.SUMMON_SFTP_URL,
                                       username=settings.SUMMON_SFTP_UN,
                                       password=settings.SUMMON_SFTP_PW) as sftp:
                    with sftp.cd('deletes'):
                        sftp.put(fh.name)
                        # write last run date to model
                        SummonDelete.objects.create(
                            date=date.today(),
                            number=number,
                            records=records
                        )
                        logger.info('Successfully uploaded the deleted records to Summon FTP server.')
