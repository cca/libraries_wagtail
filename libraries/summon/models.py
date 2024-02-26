from datetime import datetime

from django.db import models


class SummonDelete(models.Model):
    date = models.DateTimeField(
        default=datetime.now,
        help_text="Date the deleted records were sent to Summon SFTP.",
    )
    number = models.PositiveIntegerField(
        default=0, help_text="Number of records that we deleted."
    )
    records = models.TextField(
        blank=True,
        help_text='Newline-separated list of deleted record ID numbers ("biblionumber" in Koha parlance).',
    )

    def __str__(self):
        return str("{} ({})".format(self.date.strftime("%Y-%m-%d"), self.number))
