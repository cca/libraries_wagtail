"""Models for the Hours app."""

import datetime
from types import SimpleNamespace

from django.conf import settings
from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet


@register_snippet
class Library(models.Model):
    name = models.CharField(max_length=50)
    # we can expand this later with phone, address, etc.

    class Meta:
        verbose_name_plural = "libraries"

    def __str__(self):
        return self.name


# this represents a set of open hours during a typical week for a particular
# library during a date range, e.g. "Meyer Library is open 9am - 5pm Mon-Fri
# and closed Sun/Sat from 2017-06-01 to 2017-07-31"
@register_snippet
class OpenHours(models.Model):
    label = models.CharField(max_length=200, help_text="e.g. Meyer Fall 2017")

    library = models.ForeignKey(
        "hours.Library",
        on_delete=models.PROTECT,
        related_name="+",
    )

    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date")

    # I cringe but is there a better way to model this?
    # Tradeoff of using a double open/close hour integer: this is more flexible
    # because we can write in parentheticals ("no checkouts") & slightly easier
    # in templating because I can spit out the raw CharField, no processing
    # NOTE: names of fields must be weekday names from
    # datetime.strftime('%a').lower()
    mon = models.CharField(max_length=150)
    tue = models.CharField(max_length=150)
    wed = models.CharField(max_length=150)
    thu = models.CharField(max_length=150)
    fri = models.CharField(max_length=150)
    sat = models.CharField(max_length=150)
    sun = models.CharField(max_length=150)

    panels = [
        FieldPanel("label", classname="full title"),
        FieldPanel("library"),
        MultiFieldPanel(
            [
                FieldPanel("start_date", classname="col6"),
                FieldPanel("end_date", classname="col6"),
            ],
            heading="Date Range",
        ),
        MultiFieldPanel(
            [
                FieldPanel("mon", classname="col4"),
                FieldPanel("tue", classname="col4"),
                FieldPanel("wed", classname="col4"),
                FieldPanel("thu", classname="col4"),
                FieldPanel("fri", classname="col4"),
                FieldPanel("sat", classname="col4"),
                FieldPanel("sun", classname="col4"),
            ],
            heading="Weekday Hours",
        ),
    ]

    class Meta:
        verbose_name_plural = "open hours"

    def __str__(self):
        return self.label


@register_snippet
class Closure(models.Model):
    label = models.CharField(max_length=200, help_text="e.g. Simpson Fall 2022")

    library = models.ForeignKey(
        "hours.Library",
        on_delete=models.PROTECT,
        related_name="+",
    )

    start_date = models.DateField("Start Date")
    end_date = models.DateField(
        "End Date",
        help_text="can be the same as start date",
    )

    explanation = RichTextField(
        features=settings.RICHTEXT_BASIC,
        blank=True,
        help_text="This is a staff-facing field only right now.",
    )

    panels = [
        FieldPanel("label", classname="full title"),
        FieldPanel("library"),
        MultiFieldPanel(
            [
                FieldPanel("start_date", classname="col6"),
                FieldPanel("end_date", classname="col6"),
            ],
            heading="Date Range",
        ),
        FieldPanel("explanation"),
    ]

    def __str__(self):
        return self.label


# returns a dict of each library's open hours for a given date e.g.
# { meyer: '9-5', simpson: '9-6', materials: 'closed' }
# the home page uses this function
def get_open_hours(day=datetime.date.today()):
    # if we're passed a string, convert it to a date
    if isinstance(day, str):
        # validate input, default to today if we can't get a valid date
        try:
            day = datetime.datetime.strptime(day, "%Y-%m-%d")
        except ValueError:
            day = datetime.date.today()

    weekday = day.strftime("%a").lower()

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
        # "closed" default value
        output[lib.name] = "closed"
        # if there's a closure, it overrides the hours for a time period
        if lib.name not in closed_libs:
            lib_hrs = hrs.filter(library=lib)
            # avoid NoneType errors by testing
            if lib_hrs:
                output[lib.name] = lib_hrs.values_list(weekday).first()[0]

    return output


# default if we have no hours
no_hours = SimpleNamespace(
    mon="TBD",
    tue="TBD",
    wed="TBD",
    thu="TBD",
    fri="TBD",
    sat="TBD",
    sun="TBD",
)


# returns a dict of hours for a date
def get_hours_for_lib(libname, for_date=datetime.date.today()):
    hrs = OpenHours.objects.all()
    hrs = (
        hrs.filter(start_date__lte=for_date)
        .filter(end_date__gte=for_date)
        .filter(library__name=libname)
    )
    if hrs:
        hrs = hrs.first() or no_hours
        return {
            "mon": hrs.mon,
            "tue": hrs.tue,
            "wed": hrs.wed,
            "thu": hrs.thu,
            "fri": hrs.fri,
            "sat": hrs.sat,
            "sun": hrs.sun,
        }
    return None


class HoursPage(Page):
    parent_page_types = ["categories.RowComponent"]
    subpage_types = []
    max_count = 1

    intro = RichTextField(features=settings.RICHTEXT_ADVANCED, blank=True)
    main_image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
        help_text="Doesn't display on the page itself but a thumbnail close "
        "to 230x115px is used on the 'About Us' page and a smaller "
        "thumbnail is also used in search results.",
    )
    order = models.IntegerField(
        default=1,
        help_text="Defines the sort order in the parent row (lower numbers "
        "go first).",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("main_image"),
    ]
    promote_panels = Page.promote_panels + [FieldPanel("order")]

    class Meta:
        ordering = ["order", "-last_published_at"]

    # for consistency with other child pages in categories app
    def category(self):
        return "about-us"

    def get_context(self, request):
        context = super(HoursPage, self).get_context(request)
        # default to current date but allow "date" parameter in URL
        for_date = request.GET.get("date", datetime.date.today())
        hrs = {}
        for lib in Library.objects.all():
            hrs[lib.name] = get_hours_for_lib(lib.name, for_date=for_date)

        context["hours"] = hrs
        # for ease of templating, don't pass "for_date" when it's current date
        if for_date != datetime.date.today():
            context["for_date"] = datetime.datetime.strptime(for_date, "%Y-%m-%d")

        return context

    # allow only one instance of the staff list page to be created
    @classmethod
    def can_create_at(cls, parent):
        return super(HoursPage, cls).can_create_at(parent) and not cls.objects.exists()
