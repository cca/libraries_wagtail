from django.db import models
from django import forms
from django.shortcuts import redirect

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


class CategoryPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['categories.RowComponent']

    # add child RowComponent to context
    def get_context(self, request):
        context = super(CategoryPage, self).get_context(request)
        rows = self.get_children().live()
        context['rows'] = rows
        return context


class ServicePage(Page):
    parent_page_types = ['categories.RowComponent']
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
# but only used as a component of a CategoryPage
# also since the RowComponent is never directly rendered we can't use its
# get_context() method to retrieve child pages, that has to be done in template
class RowComponent(Page):
    parent_page_types = ['categories.CategoryPage']
    subpage_types = ['categories.ServicePage']
    # this can't be RichTextField or the template screws up
    summary = models.CharField(max_length=350)
    # do not index for search
    search_fields = []
    # no need for a promote tab since slug & search_desc aren't used
    promote_panels = []

    content_panels = Page.content_panels + [
        FieldPanel('summary'),
    ]

    # if a row is requested, redirect to its parent page instead
    def serve(self, request):
        parent = self.get_parent()
        return redirect(parent.url)


class SpecialCollectionsPage(Page):
    parent_page_types = ['categories.CategoryPage']
    # right now, no child special collection pages, but could add in the future
    subpage_types = []

    # needs an orderable struct of some sort which contains a title, richtext blurb,
    # link to the external collection, and feature image _at least_
    content_panels = Page.content_panels + [
        InlinePanel('special_collections', label='Special Collection')
    ]

    # @TODO needs a main_image for search...maybe a method that returns
    # the first image from a child SpecialCollection?

    # make page searchable by text of child special collections
    search_fields = [
        index.RelatedFields('special_collections', [
            index.SearchField('title'),
            index.SearchField('blurb'),
        ]),
    ]


class SpecialCollection(Orderable):
    page = ParentalKey(SpecialCollectionsPage, related_name='special_collections')
    title = models.CharField(max_length=255)
    # RichTextField allows links & text formatting so this is questionable
    blurb = RichTextField()
    # URLField lets this link be either internal or external
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
    parent_page_types = ['categories.CategoryPage']

    # only fields are likely to be a featured image
    # and a stream field for text, pull quotes, images, etc.
    # similar to a blog post
