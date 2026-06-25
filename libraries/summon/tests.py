import datetime
from unittest.mock import MagicMock, patch
from urllib.parse import quote

from django.conf import settings
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from summon.models import SummonDelete


@override_settings(
    SUMMON_SFTP_UN="test_sftp_user",
    SUMMON_SFTP_HOST="test.sftp.host",
    SUMMON_REPORT_URL="https://test.report.url/report?id=152&sql_params={}",
)
class TestSummonDeletesCommand(TestCase):
    """Tests for the summon_deletes management command."""

    @patch("summon.management.commands.summon_deletes.Path.exists")
    def test_missing_ssh_key(self, mock_exists):
        """Test that CommandError is raised if the CDI key does not exist."""
        mock_exists.return_value = False
        with self.assertRaises(CommandError) as ctx:
            call_command("summon_deletes")
        self.assertIn("Requires the CDI private key", str(ctx.exception))

    @patch("summon.management.commands.summon_deletes.Path.exists")
    def test_invalid_lastrun_date_format(self, mock_exists):
        """Test that CommandError is raised if lastrun date format is invalid."""
        mock_exists.return_value = True
        with self.assertRaises(CommandError) as ctx:
            call_command("summon_deletes", "invalid-date")
        self.assertIn("Invalid lastrun date", str(ctx.exception))

    @patch("summon.management.commands.summon_deletes.Path.exists")
    def test_missing_lastrun_and_no_database_records(self, mock_exists):
        """Test that CommandError is raised when lastrun is omitted and database is empty."""
        mock_exists.return_value = True
        SummonDelete.objects.all().delete()
        with self.assertRaises(CommandError) as ctx:
            call_command("summon_deletes")
        self.assertIn("There are no SummonDelete objects", str(ctx.exception))

    @patch("summon.management.commands.summon_deletes.Path.exists")
    @patch("summon.management.commands.summon_deletes.requests.get")
    def test_no_deletions_found(self, mock_get, mock_exists):
        """Test command when Koha returns no deleted records (empty list)."""
        mock_exists.return_value = True

        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        with self.assertRaises(SystemExit) as cm:
            call_command("summon_deletes", "2026-06-01")
        self.assertEqual(cm.exception.code, 0)

        # Verify no database entry was created
        self.assertEqual(SummonDelete.objects.count(), 0)

    @patch("summon.management.commands.summon_deletes.Path.exists")
    @patch("summon.management.commands.summon_deletes.requests.get")
    @patch("summon.management.commands.summon_deletes.SSHClient")
    def test_successful_run(self, mock_ssh_client_class, mock_get, mock_exists):
        """Test successful execution: fetches report, uploads to SFTP, creates DB log."""
        mock_exists.return_value = True

        # Mock Koha response returning 2 deleted record IDs
        mock_response = MagicMock()
        mock_response.json.return_value = [[12345], [67890]]
        mock_get.return_value = mock_response

        # Mock SSH Client and SFTP Client
        mock_ssh_client = MagicMock()
        mock_sftp_client = MagicMock()
        mock_ssh_client.open_sftp.return_value.__enter__.return_value = mock_sftp_client
        mock_ssh_client_class.return_value.__enter__.return_value = mock_ssh_client

        # Call command
        call_command("summon_deletes", "2026-06-01")

        # Verify requests.get was called with formatted date
        expected_url = settings.SUMMON_REPORT_URL.format(quote("20260601"))
        mock_get.assert_called_once_with(expected_url)

        # Verify SSH connection and SFTP put operations
        mock_ssh_client.connect.assert_called_once_with(
            hostname=settings.SUMMON_SFTP_HOST,
            port=10022,
            username=settings.SUMMON_SFTP_UN,
            key_filename="/root/.ssh/cdi_cca.key",
        )
        mock_sftp_client.chdir.assert_called_once_with("deletes")
        mock_sftp_client.put.assert_called_once()

        put_args = mock_sftp_client.put.call_args[0]
        self.assertTrue(put_args[0].endswith("cca-catalog-deletes-2026-06-01.mrc"))
        self.assertEqual(put_args[1], "cca-catalog-deletes-2026-06-01.mrc")

        # Verify that a SummonDelete log record was created
        self.assertEqual(SummonDelete.objects.count(), 1)
        log = SummonDelete.objects.first()
        self.assertIsNotNone(log)
        self.assertEqual(log.number, 2)  # type: ignore
        self.assertEqual(log.records, "12345\n67890")  # type: ignore
        self.assertAlmostEqual(
            log.date,  # type: ignore
            timezone.now(),
            delta=datetime.timedelta(seconds=5),  # type: ignore
        )
