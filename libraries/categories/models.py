from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


class ServicesPage(Page):
    parent_page_types = ['home.HomePage']

    # this one's a bit trickier—how can we represent a series of services from a
    # controlled list of service_types (InST, Circ, Tech Support)? It kind of looks like
    # an orderable category struct with title, blurb, which then contains a _child_
    # orderable struct for each individual service and has a title, sentence, &
    # (optional?) thumbnail

    # allow only one instance of this page type
    @classmethod
    def can_create_at(cls, parent):
        return super(ServicesPage, cls).can_create_at(parent) and not cls.objects.exists()


class CollectionsPage(Page):
    parent_page_types = ['home.HomePage']
    # right now, no child collection pages, they all point external
    # we'll almost certainly need to revisit this & make a subpage
    # that can be referenced via the collection.link URLField
    subpage_types = []

    # needs an orderable struct of some sort which cnotains a title, richtext blurb,
    # link to the external collection, and feature image _at least_
    content_panels = Page.content_panels + [
        InlinePanel('collections', label='collection')
    ]

    # allow only one instance of this page type
    @classmethod
    def can_create_at(cls, parent):
        return super(CollectionsPage, cls).can_create_at(parent) and not cls.objects.exists()


class Collection(Orderable):
    page = ParentalKey(CollectionsPage, related_name='collections')
    title = models.CharField(max_length=255)
    # RichTextField allows links & text formatting so this is questionable
    blurb = RichTextField()
    # URLField lets this link either internally or externally
    link = models.URLField()
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('blurb'),
        FieldPanel('link'),
        ImageChooserPanel('image'),
    ]


class AboutUsPage(Page):
    parent_page_types = ['home.HomePage']

    # only fields are likely to be a featured image
    # and a stream field for text, pull quotes, images, etc.
    # similar to a blog post

    # allow only one instance of this page type
    @classmethod
    def can_create_at(cls, parent):
        return super(AboutUsPage, cls).can_create_at(parent) and not cls.objects.exists()
