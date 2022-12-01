import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

import pysftp
import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from summon.models import SummonDelete

logger = logging.getLogger('mgmt_cmd.script')
key_path = Path('/root/.ssh/cdi_cca.key')


class Command(BaseCommand):
    help = "Send a list of deleted bib records to the Summon SFTP server so they can be removed from our discovery index. This command is meant to be run on a schedule."

    def add_arguments(self, parser):
        parser.add_argument('lastrun', nargs='?', type=str,
                            help='date of last run (in MM/DD/YYYY format)')

    def handle(self, **options):
        if not Path.exists(key_path):
            raise CommandError(f"Requires the CDI private key to be located at {key_path}")
        # lastrun is a STRING (not date!) of form "MM/DD/YYYY"
        try:
            lastrun = options.get('lastrun', None) or SummonDelete.objects.latest('date').date.strftime('%m/%d/%Y')
        except SummonDelete.DoesNotExist:
            # on the first run the above will raise an error because there are
            # no SummonDelete.objects yet
            logger.error('There are no existing SummonDelete objects. Please run this management script with an argument of the date we last updated Summon in "MM/DD/YYYY" format.')
            exit(1)
        logger.info("Finding deleted MARC records since {}".format(lastrun))

        response = requests.get(settings.SUMMON_REPORT_URL.format(quote("'{}'".format(lastrun))))
        # Koha JSON is an array of arrays for each row of the report e.g. [[1], [2]]
        rows = response.json()
        number = len(rows)
        # unpack the record sub-lists into a newline-delimited string
        records = '\n'.join([str(rec) for [rec] in rows])
        logger.info("{} records were deleted since {}".format(number, lastrun))

        # write records text list to file in temporary directory
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cca-catalog-deletes-{}.mrc".format(lastrun.replace('/', '-'))
            with path.open('w+') as fh:
                fh.write(records)

            # PUT file to Summon SFTP server
            with pysftp.Connection(settings.SUMMON_SFTP_HOST, port=10022,
                private_key=key_path, username=settings.SUMMON_SFTP_UN) as sftp:
                with sftp.cd('deletes'):
                    sftp.put(fh.name)
                    # write last run date to model
                    SummonDelete.objects.create(
                        date=timezone.now(),
                        number=number,
                        records=records
                    )
                    logger.info('Successfully uploaded the deleted records to Summon FTP server.')
