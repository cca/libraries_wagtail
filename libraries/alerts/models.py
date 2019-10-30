from django.db import models

from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField

# See https://github.com/cca/portal/blob/3860bd2e8b436a6aa62d475adc3785832c99a1e1/portal/apps/cms/models/pages.py
# We need AlertPage & NotificationPage defined ultimately but those rely on a
# lot of other Portal models
class AbstractAlertPage(models.Model):
    alert_page_body = StreamField(ALERT_PAGE_STREAM_FIELD_ELEMENTS, blank=True, null=True)
    content_panels = [StreamFieldPanel('alert_page_body')]

    @property
    def body_text(self):
        body_text = []
        for block in self.body:
            if block.block_type in ['subheading', 'paragraph']:
                try:
                    body_text.append(block.value.source)
                except AttributeError:
                    pass  # block does not have value.source
        return "".join(body_text)

    class Meta:
        abstract = True


class CcaEduApiToken(models.Model):
    """
    Store cca.edu JWT token for accessing cca.edu API
    """
    access_token = models.TextField(null=False, blank=False)
    datetime_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'datetime_added'
