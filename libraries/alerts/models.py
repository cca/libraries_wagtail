from django.db import models
from django.utils.translation import gettext_lazy as _


class Alert(models.Model):
    '''
    Alert model, syncs from portal.cca.edu.
    '''
    id = models.PositiveIntegerField(primary_key=True, help_text="This should be the same as the Portal ID.")
    last_published_at = models.DateTimeField(
        verbose_name=_('last published at'),
        null=True,
        editable=False
    )
    alert_text = models.TextField(help_text="Add text that will appear on the alert bannner. Maximum 500 characters")
    alert_link = models.URLField(blank=True, null=True, default="", help_text="Optional link to portal.cca.edu alert page.")
    alert_link_text = models.CharField(
        max_length=255, default="More Info",
        help_text="The text that will appear in the alert banner or the link to this Alert Page, if applicable."
    )

    def show_read_more(self):
        return bool(self.alert_link)
