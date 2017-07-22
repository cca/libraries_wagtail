from django.db import models
from django import forms
from django.shortcuts import redirect

from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

from wagtail.wagtailcore.blocks import StructBlock, StreamBlock, CharBlock, FieldBlock, RichTextBlock, TextBlock, RawHTMLBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock


# @TODO we don't use this right now but it's here waiting to be added
# to ImageBlock() if need be
class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'),
        ('right', 'Wrap right'),
        ('mid', 'Mid width'),
        ('full', 'Full width'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock(blank=True)
    # alignment = ImageFormatChoiceBlock()

    class Meta:
        icon = "image"
        template = "categories/blocks/image.html"


class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    name = CharBlock(blank=True)
    position = CharBlock(blank=True, label="Position or affiliation")

    class Meta:
        icon = "openquote"
        template = "categories/blocks/quote.html"


# no need for a template as raw HTML is what we want
class EmbedHTML(RawHTMLBlock):
    html = RawHTMLBlock(
        "Embed code or raw HTML",
        help_text='Use this sparingly, if possible.',
    )


class BaseStreamBlock(StreamBlock):
    subheading = CharBlock(
        icon="title",
        classname="title",
        template="categories/blocks/subheading.html"
    )
    paragraph = RichTextBlock(
        template="categories/blocks/paragraph.html",
        icon="pilcrow",
    )
    image = ImageBlock()
    pullquote = PullQuoteBlock()
    snippet = RichTextBlock(template="categories/blocks/snippet.html")
    html = EmbedHTML(label="Embed code")


class CategoryPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = [
        'categories.RowComponent',
        'categories.AboutUsPage',
    ]

    # add child RowComponent to context
    def get_context(self, request):
        context = super(CategoryPage, self).get_context(request)
        rows = self.get_children().live()
        context['rows'] = rows
        return context


# @TODO we don't have a template for this type of page
# should it reuse BlogPage or AboutUsPage?
# also it needs an image for search results
class ServicePage(Page):
    parent_page_types = ['categories.RowComponent']
    # may need to revisit this but for now no children of service pages
    subpage_types = []
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Try to ALWAYS provide a main image.'
    )
    body = StreamField(
        BaseStreamBlock(),
        verbose_name='Page content',
        null=True
    )
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
    subpage_types = [
        'categories.ServicePage',
        'categories.AboutUsPage',
        'categories.SpecialCollectionsPage',
    ]
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


# Another child of RowComponent but with a very different structure & template
class SpecialCollectionsPage(Page):
    parent_page_types = ['categories.RowComponent']
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

# ServicePage & AboutUsPage are basically two different templates for the same
# sort of grandchild content (CategoryPage > RowComponent > Service/AboutUsPage)
class AboutUsPage(Page):
    parent_page_types = ['categories.RowComponent']
    # we allow nested about us pages
    subpage_types = ['categories.AboutUsPage']
    body = StreamField(
            BaseStreamBlock(),
            verbose_name='Page content',
            null=True,
    )
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Try to ALWAYS provide a main image.'
    )
    search_fields = Page.search_fields + [ index.SearchField('body') ]

    content_panels = Page.content_panels + [
        ImageChooserPanel('main_image'),
        StreamFieldPanel('body'),
    ]
