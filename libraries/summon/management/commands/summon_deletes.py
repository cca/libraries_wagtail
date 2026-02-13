import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from paramiko import SSHClient

from summon.models import SummonDelete

logger = logging.getLogger("mgmt_cmd.script")
key_path = Path("/root/.ssh/cdi_cca.key")


class Command(BaseCommand):
    help = "Send a list of deleted bib records to the Summon SFTP server so they can be removed from our discovery index. This command is intended to run on a schedule."

    def add_arguments(self, parser):
        parser.add_argument(
            "lastrun",
            nargs="?",
            type=str,
            help="date of last run (in MM/DD/YYYY format)",
        )

    def handle(self, **options):
        if not Path.exists(key_path):
            raise CommandError(
                f"Requires the CDI private key to be located at {key_path}"
            )
        try:
            lastrun: str = options.get("lastrun", "") or SummonDelete.objects.latest(
                "date"
            ).date.strftime("%Y-%m-%d")
        except SummonDelete.DoesNotExist:
            # on the first run the above will raise an error because there are
            # no SummonDelete.objects yet
            logger.error(
                'There are no existing SummonDelete objects. Please run this management script with an argument of the date we last updated Summon in "MM/DD/YYYY" format.'
            )
            exit(1)
        logger.info(f"Finding deleted MARC records since {lastrun}")

        response = requests.get(settings.SUMMON_REPORT_URL.format(quote(f"{lastrun}")))
        # Koha JSON is an array of arrays for each row of the report e.g. [[1], [2]]
        rows: list[list[int]] = response.json()
        number: int = len(rows)

        if number == 0:
            logger.info(
                f"No records were deleted since {lastrun}, not sending data to Summon"
            )
            exit(0)

        logger.info(f"{number} records were deleted since {lastrun}")
        # unpack the record sub-lists into a newline-delimited string
        records = "\n".join([str(rec) for [rec] in rows])

        # write records text list to file in temporary directory
        with TemporaryDirectory() as tmpdir:
            path: Path = (
                Path(tmpdir) / f"cca-catalog-deletes-{lastrun.replace('/', '-')}.mrc"
            )
            with path.open("w+") as fh:
                fh.write(records)

            # PUT file to Summon SFTP server
            # https://docs.paramiko.org/en/stable/api/client.html
            with SSHClient() as ssh_client:
                ssh_client.load_system_host_keys()
                ssh_client.connect(
                    hostname=settings.SUMMON_SFTP_HOST,
                    port=10022,
                    username=settings.SUMMON_SFTP_UN,
                    key_filename=str(key_path),
                )
                # https://docs.paramiko.org/en/stable/api/sftp.html#paramiko.sftp_client.SFTPClient
                with ssh_client.open_sftp() as sftp:
                    sftp.chdir("deletes")
                    sftp.put(str(path), path.name, confirm=True)

        # write last run date to model
        SummonDelete.objects.create(date=timezone.now(), number=number, records=records)
        logger.info("Successfully uploaded the deleted records to Summon FTP server.")
