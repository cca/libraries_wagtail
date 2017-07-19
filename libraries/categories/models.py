from django.db import models
from django import forms

from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

from wagtail.wagtailcore.blocks import StructBlock, StreamBlock, CharBlock, FieldBlock, RichTextBlock, TextBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock


# @TODO we don't use this right now but it's here waiting to be added
# to ImageBlock() if need be
class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()
    # alignment = ImageFormatChoiceBlock()

    class Meta:
        icon = "image"


class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        icon = "openquote"


class BaseStreamBlock(StreamBlock):
    subheading = CharBlock(icon="title", classname="title")
    paragraph = RichTextBlock(icon="pilcrow")
    image = ImageBlock()
    pullquote = PullQuoteBlock()
    snippet = RichTextBlock()


class ServicesPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['categories.ServicesRowPage']

    # add child ServicesRowPage to context
    def get_context(self, request):
        context = super(ServicesPage, self).get_context(request)
        rows = self.get_children().live()
        context['services_rows'] = rows
        return context

    # allow only one instance of this page type
    @classmethod
    def can_create_at(cls, parent):
        return super(ServicesPage, cls).can_create_at(parent) and not cls.objects.exists()


class ServicePage(Page):
    parent_page_types = ['categories.ServicesRowPage']
    subpage_types = []
    # @TODO _here_ is the spot for some streamfields I think
    # reuse about_us_page template most likely
    body = StreamField(BaseStreamBlock())
    search_fields = Page.search_fields + [ index.SearchField('body') ]

    # @TODO related staff member

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]


# does not have a matching template, should never be visited on its own
# but only used as a component of ServicesPage
# also since the ServicesRowPage is never directly rendered we can't use its
# get_context() method to retrieve child services, that has to be done in template
class ServicesRowPage(Page):
    parent_page_types = ['categories.ServicesPage']
    subpage_types = ['categories.ServicePage']
    # this can't be RichTextField or the template screws up
    summary = models.CharField(max_length=350)
    # do not index for search
    search_fields = []

    content_panels = Page.content_panels + [
        FieldPanel('summary'),
    ]


class CollectionsPage(Page):
    parent_page_types = ['home.HomePage']
    # right now, no child collection pages, they all point external
    # we'll almost certainly need to revisit this & make a subpage
    # that can be referenced via the collection.link URLField
    subpage_types = []

    # needs an orderable struct of some sort which contains a title, richtext blurb,
    # link to the external collection, and feature image _at least_
    content_panels = Page.content_panels + [
        InlinePanel('collections', label='collection')
    ]

    # make collections page searchable by text of specific collections
    search_fields = [
        index.RelatedFields('collections', [
            index.SearchField('title'),
            index.SearchField('blurb'),
        ]),
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
