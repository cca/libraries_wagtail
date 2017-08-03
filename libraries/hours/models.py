import datetime

from django.db import models

from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page


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
    mon = models.CharField(max_length=150)
    tue = models.CharField(max_length=150)
    wed = models.CharField(max_length=150)
    thu = models.CharField(max_length=150)
    fri = models.CharField(max_length=150)
    sat = models.CharField(max_length=150)
    sun = models.CharField(max_length=150)

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

# returns a dict of each library's open hours for a given date e.g.
# { meyer: '9-5', simpson: '9-6', materials: 'closed' }
# the home page uses this function
def get_open_hours(day=datetime.date.today()):
    # if we're passed a string, convert it to a date
    if type(day) is str:
        # @TODO validate input, must match \d{4}-\d{2}-\d{2} regex
        day = datetime.datetime.strptime(day, '%Y-%m-%d')

    weekday = day.strftime('%a').lower()

    hrs = OpenHours.objects.all()
    # filter to open hours that contain the given day
    hrs = hrs.filter(start_date__lte=day).filter(end_date__gte=day)

    closures = Closure.objects.all()
    closures = closures.filter(start_date__lte=day).filter(end_date__gte=day)
    # closures should just be a list of closed library names
    closed_libs = []
    for closure in closures:
        closed_libs.append(closure.library.name)

    output = {}
    # iterate over all Library snippets
    for lib in Library.objects.all():
        # initialize with a null fallback value
        output[lib.name] = ''
        # register closures first, they override hours for a given date
        if lib.name in closed_libs:
            output[lib.name] = 'closed'
        else:
            lib_hrs = hrs.filter(library=lib)
            # avoid NoneType errors by testing
            if lib_hrs:
                output[lib.name] = lib_hrs.values_list(weekday).first()[0]

    return output


def get_hours_for_lib(libname):
    today = datetime.date.today()
    hrs = OpenHours.objects.all()
    hrs = hrs.filter(start_date__lte=today).filter(end_date__gte=today).filter(library__name=libname)
    if not hrs:
        return None
    else:
        return hrs.first()


class HoursPage(Page):
    parent_page_types = ['categories.RowComponent']
    subpage_types = []

    intro = RichTextField(blank=True)
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='+',
        help_text='Only used in search results',
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        ImageChooserPanel('main_image'),
    ]

    # for consistency with other child pages in categories app
    def category(self):
        return 'about-us'

    def get_context(self, request):
        context = super(HoursPage, self).get_context(request)
        today = datetime.date.today()
        hrs = {}
        for lib in ('Meyer', 'Simpson', 'Materials'):
            hrs[lib] = get_hours_for_lib(lib)

        context['hours'] = hrs

        return context

    # allow only one instance of the staff list page to be created
    @classmethod
    def can_create_at(cls, parent):
        return super(HoursPage, cls).can_create_at(parent) and not cls.objects.exists()
