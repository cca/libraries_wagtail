from django.db import models

from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailcore.fields import RichTextField


@register_snippet
class Library(models.Model):
    name = models.CharField(max_length=50)
    # we can expand this later with phone, address, etc.

    class Meta:
        verbose_name_plural = 'libraries'

    def __str__(self):
        return self.name


# this represents a set of open hours during a typical week for a particular
# library during a date range, e.g. "Meyer Library is open 9am - 5pm Mon-Fri
# and closed Sun/Sat from 2017-06-01 to 2017-07-31"
@register_snippet
class OpenHours(models.Model):
    label = models.CharField(max_length=200, help_text="e.g. Meyer Fall 2017")

    library = models.ForeignKey(
        'hours.Library',
        on_delete=models.PROTECT,
        related_name='+',
    )

    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date")

    # I cringe but is there a better way to model this?
    # Tradeoff of using a double open/close hour integer: this is more flexible
    # because we can write in parentheticals ("no checkouts") & slightly easier
    # in templating because I can just spit out the raw CharField, no processing
    # NOTE: names of fields must be weekday names from datetime.strftime('%a').lower()
    mon = models.CharField(max_length=150, blank=True)
    tue = models.CharField(max_length=150, blank=True)
    wed = models.CharField(max_length=150, blank=True)
    thu = models.CharField(max_length=150, blank=True)
    fri = models.CharField(max_length=150, blank=True)
    sat = models.CharField(max_length=150, blank=True)
    sun = models.CharField(max_length=150, blank=True)

    panels = [
        FieldPanel('label', classname="full title"),
        SnippetChooserPanel('library'),
        MultiFieldPanel([
            FieldPanel('start_date', classname="col6"),
            FieldPanel('end_date', classname="col6"),
        ], heading="Date Range"),
        MultiFieldPanel([
            FieldPanel('mon', classname="col4"),
            FieldPanel('tue', classname="col4"),
            FieldPanel('wed', classname="col4"),
            FieldPanel('thu', classname="col4"),
            FieldPanel('fri', classname="col4"),
            FieldPanel('sat', classname="col4"),
            FieldPanel('sun', classname="col4"),
        ], heading="Weekday Hours"),
    ]

    class Meta:
        verbose_name_plural = 'open hours'

    def __str__(self):
        return self.label


@register_snippet
class Closure(models.Model):
    label = models.CharField(max_length=200, help_text="e.g. Meyer Fall 2017")

    library = models.ForeignKey(
        'hours.Library',
        on_delete=models.PROTECT,
        related_name='+',
    )

    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date",
        help_text="can be the same as start date",)

    explanation = RichTextField(blank=True)

    panels = [
        FieldPanel('label', classname="full title"),
        SnippetChooserPanel('library'),
        MultiFieldPanel([
            FieldPanel('start_date', classname="col6"),
            FieldPanel('end_date', classname="col6"),
        ], heading="Date Range"),
        FieldPanel('explanation'),
    ]

    def __str__(self):
        return self.label
