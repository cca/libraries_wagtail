import inspect

from django.conf import settings
from django.db import models
from django import forms
from django.shortcuts import redirect, render

from modelcluster.fields import ParentalKey

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, InlinePanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.search import index

from wagtail.core.blocks import StructBlock, StreamBlock, CharBlock, FieldBlock, RichTextBlock, TextBlock, RawHTMLBlock, URLBlock
from wagtail.images.blocks import ImageChooserBlock


# we don't use this right now but it's here waiting to be added
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
    caption = RichTextBlock(features=settings.RICHTEXT_BASIC, required=False)
    # alignment = ImageFormatChoiceBlock()

    class Meta:
        icon = "image"
        template = "categories/blocks/image.html"


class LinkedImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock(features=settings.RICHTEXT_BASIC, required=False)
    # alignment = ImageFormatChoiceBlock()
    link = URLBlock()

    class Meta:
        icon = "link"
        template = "categories/blocks/linked-image.html"


class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    name = CharBlock(required=False)
    position = CharBlock(required=False, label="Position or affiliation")

    class Meta:
        icon = "openquote"
        template = "categories/blocks/quote.html"


# no need for a template as raw HTML is what we want
class EmbedHTML(RawHTMLBlock):
    html = RawHTMLBlock(
        "Embed code or raw HTML",
        help_text='Use this sparingly, if possible.',
    )

# two blocks combined in one row
class RowBlock(StreamBlock):
    paragraph = RichTextBlock(
        features=settings.RICHTEXT_ADVANCED,
        template="categories/blocks/paragraph.html",
        icon="pilcrow",
    )
    image = ImageBlock()
    linked_image = LinkedImageBlock()
    pullquote = PullQuoteBlock()
    # questionable that this should be advanced HTML but we use callouts a lot
    snippet = RichTextBlock(
        features=settings.RICHTEXT_ADVANCED,
        label="Callout",
        template="categories/blocks/snippet.html")

    class Meta:
        help_text = "First child block is given 40% of the row width while the 2nd gets 60%."
        icon = 'form'
        template = "categories/blocks/row.html"


class BaseStreamBlock(StreamBlock):
    subheading = CharBlock(
        icon="title",
        classname="title",
        template="categories/blocks/subheading.html"
    )
    paragraph = RichTextBlock(
        features=settings.RICHTEXT_ADVANCED,
        template="categories/blocks/paragraph.html",
        icon="pilcrow",
    )
    image = ImageBlock()
    linked_image = LinkedImageBlock()
    pullquote = PullQuoteBlock()
    snippet = RichTextBlock(label="Callout", template="categories/blocks/snippet.html")
    html = EmbedHTML(label="Embed code")
    row = RowBlock(max_num=2)

# AboutUsPage has a much simpler template
class AboutUsStreamBlock(StreamBlock):
    paragraph = RichTextBlock(
        features=settings.RICHTEXT_ADVANCED,
        icon="pilcrow",
    )

# helper method—for child pages, return their category i.e. parent CategoryPage
# one of: services, collections, about us
def get_category(page):
    return page.get_ancestors().type(CategoryPage).first()


class CategoryPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = [
        'categories.RowComponent',
        'categories.AboutUsPage',
    ]

    # add child RowComponent(s) to context
    def get_context(self, request):
        # if this is a preview of a draft RowComponent, include the draft
        if request.GET.get('DRAFT'):
            context = self.get_context(request)
            rows = self.get_children()
        else:
            context = super(CategoryPage, self).get_context(request)
            rows = self.get_children().live()
        context['rows'] = rows
        return context


# reuses blocks from the BlogPage template
class ServicePage(Page):
    parent_page_types = [
        'categories.RowComponent',
        'categories.ServicePage',
        'categories.AboutUsPage',
        'categories.SpecialCollectionsPage',
    ]
    subpage_types = [
        'categories.ServicePage',
        'categories.AboutUsPage',
        'categories.SpecialCollectionsPage',
    ]
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='+',
        help_text='Displays 404px wide on page with a preserved aspect ratio. If this page shows in one of the Services/Collections/About rows, a thumbnail close to 230x115px is generated.'
    )
    staff = models.ForeignKey(
        'staff.StaffMember',
        blank=True,
        help_text='Optional associated staff member',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    display_staff_card = models.BooleanField(default=False, help_text='Display a small "card" showing contact information for the associated staff member.')
    body = StreamField(
        BaseStreamBlock(),
        verbose_name='Page content',
        null=True,
    )
    search_fields = Page.search_fields + [ index.SearchField('body') ]


    def category(self):
        return get_category(self)


    class Meta:
        verbose_name = 'Complex text page'

    content_panels = Page.content_panels + [
        ImageChooserPanel('main_image'),
        FieldRowPanel(
            (SnippetChooserPanel('staff'), FieldPanel('display_staff_card'),)
        ),
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
        'categories.ExternalLink',
        'staff.StaffListPage',
        'hours.HoursPage',
    ]
    summary = RichTextField(features=settings.RICHTEXT_BASIC)
    # do not index for search
    search_fields = []
    # no need for a promote tab since slug & search_desc aren't used
    promote_panels = []

    content_panels = Page.content_panels + [
        FieldPanel('summary'),
    ]


    def category(self):
        return get_category(self)

    # if a row is requested, redirect to its parent CategoryPage instead
    def serve(self, request):
        parent = self.get_parent()
        return redirect(parent.url)

    # rendering drafts is complicated, we need to let the parent know to
    # include draft RowComponents in its context
    def serve_preview(self, request, mode_name):
        parent = self.get_parent()
        request.GET = request.GET.copy()
        request.GET['DRAFT'] = True
        ctx = CategoryPage.get_context(parent, request)
        return render(request, 'categories/category_page.html', context=ctx)

# Another child of RowComponent but with a very different structure & template
class SpecialCollectionsPage(Page):
    parent_page_types = [
        'categories.RowComponent',
        'categories.ServicePage',
        'categories.AboutUsPage',
        'categories.SpecialCollectionsPage',
    ]
    subpage_types = [
        'categories.ServicePage',
        'categories.AboutUsPage',
        'categories.SpecialCollectionsPage',
    ]

    # needs an orderable struct of some sort which contains a title, richtext blurb,
    # link to the external collection, and feature image _at least_
    content_panels = Page.content_panels + [
        InlinePanel('special_collections', label='Special Collection')
    ]

    # for search results—treat first SpecialCollection image as the page's image
    @property
    def main_image(self):
        return self.specific.special_collections.first().image

    def category(self):
        return get_category(self)

    # make page searchable by text of child special collections
    search_fields = Page.search_fields + [
        index.RelatedFields('special_collections', [
            index.SearchField('title'),
            index.SearchField('blurb'),
        ]),
    ]


class SpecialCollection(Orderable):
    page = ParentalKey(SpecialCollectionsPage, related_name='special_collections')
    title = models.CharField(max_length=255)
    blurb = RichTextField(features=settings.RICHTEXT_BASIC)
    # URLField lets this link be either internal or external
    # Per Teri on 2017-08-09: some Spaces on a SpecColl page have no links
    link = models.URLField(blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        help_text='Close to a 2.25-by-1 aspect ratio is bst, image is sized to 910x400px at its largest.',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+'
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('blurb'),
        FieldPanel('link'),
        ImageChooserPanel('image'),
    ]

# ServicePage & AboutUsPage are two different templates for the same
# sort of grandchild content (CategoryPage > RowComponent > Service/AboutUsPage)
class AboutUsPage(Page):
    parent_page_types = [
        'categories.RowComponent',
        'categories.ServicePage',
        'categories.AboutUsPage',
        'categories.SpecialCollectionsPage',
    ]
    subpage_types = [
        'categories.ServicePage',
        'categories.AboutUsPage',
        'categories.SpecialCollectionsPage',
    ]
    body = StreamField(
        AboutUsStreamBlock(),
        verbose_name='Page content',
        null=True,
    )
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='+',
        help_text='Displays 404px wide on page with a preserved aspect ratio. If this page shows in one of the Services/Collections/About rows, a thumbnail close to 230x115px is generated.',
    )
    staff = models.ForeignKey(
        'staff.StaffMember',
        blank=True,
        help_text='Optional associated staff member',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    search_fields = Page.search_fields + [ index.SearchField('body') ]

    content_panels = Page.content_panels + [
        ImageChooserPanel('main_image'),
        SnippetChooserPanel('staff'),
        StreamFieldPanel('body'),
    ]


    def category(self):
        return get_category(self)

    class Meta:
        verbose_name = 'Simple text page'


class ExternalLink(Page):
    # only used for linking items in a row to external locations
    parent_page_types = [
        'categories.RowComponent',
    ]
    # external link goes off the site, cannot have children
    subpage_types = []

    link = models.URLField(blank=False)

    staff = models.ForeignKey(
        'staff.StaffMember',
        blank=True,
        help_text='Optional associated staff member',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        help_text='If this page shows in one of the Services/Collections/About rows, a thumbnail close to 230x115px is generated.',
        null=True,
        on_delete=models.PROTECT,
        related_name='+',
    )

    # no need for a promote, search_desc is on content & slug isn't used
    promote_panels = []

    content_panels = Page.content_panels + [
        FieldPanel('link'),
        FieldPanel('search_description'),
        ImageChooserPanel('main_image'),
        SnippetChooserPanel('staff'),
    ]

    # redirect to external URL
    def serve(self, request):
        return redirect(self.link)
