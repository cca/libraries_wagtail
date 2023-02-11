from django.conf import settings
from django.db import models

from django.shortcuts import redirect, render

from wagtail.api import APIField

from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, StreamFieldPanel
from wagtail.core.blocks import StreamBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from categories.models.blocks import *
from libraries.utils import validate_clean


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

    def clean(self):
        super().clean()
        validate_clean(self)


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
    sidebar_cards = StreamField(
        StreamBlock([('card', SidebarCardBlock())], required=False),
        verbose_name='Cards in the right-hand column',
        blank=True, null=True,
    )
    resources = StreamField(
        StreamBlock([('link', LinkBlock())], required=False),
        verbose_name='List of resource links',
        blank=True, null=True,
    )
    order = models.IntegerField(
        default=1,
        help_text='Defines the sort order in the parent row (lower numbers go first).',
    )
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('sidebar_cards'),
        index.SearchField('resources'),
    ]

    def category(self):
        return get_category(self)

    def clean(self):
        super().clean()
        validate_clean(self)

    class Meta:
        verbose_name = 'Complex text page'

    content_panels = Page.content_panels + [
        ImageChooserPanel('main_image'),
        FieldRowPanel(
            (SnippetChooserPanel('staff'), FieldPanel('display_staff_card'),)
        ),
        StreamFieldPanel('body'),
        StreamFieldPanel('sidebar_cards'),
        StreamFieldPanel('resources'),
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel('order')
    ]
    api_fields = [
        APIField('body'),
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
    # no need for a promote tab since slug & search_desc aren't used
    promote_panels = []

    content_panels = Page.content_panels + [
        FieldPanel('summary'),
    ]

    # do not index for search
    def get_indexed_instance(self):
        return None

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
    display_staff_card = models.BooleanField(default=False, help_text='Display a small "card" showing contact information for the associated staff member.')
    body = StreamField(
        AboutUsStreamBlock(),
        verbose_name='Page content',
        null=True,
    )
    sidebar_cards = StreamField(
        StreamBlock([('card', SidebarCardBlock())], required=False),
        verbose_name='Cards in the right-hand column',
        blank=True, null=True,
    )
    resources = StreamField(
        StreamBlock([('link', LinkBlock())], required=False),
        verbose_name='List of resource links',
        blank=True, null=True,
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
    order = models.IntegerField(
        default=1,
        help_text='Defines the sort order in the parent row (lower numbers go first).',
    )
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('sidebar_cards'),
        index.SearchField('resources'),
    ]

    content_panels = Page.content_panels + [
        ImageChooserPanel('main_image'),
        FieldRowPanel(
            (SnippetChooserPanel('staff'), FieldPanel('display_staff_card'),)
        ),
        StreamFieldPanel('body'),
        StreamFieldPanel('sidebar_cards'),
        StreamFieldPanel('resources'),
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel('order')
    ]
    api_fields = [
        APIField('body'),
    ]

    def category(self):
        return get_category(self)

    def clean(self):
        super().clean()
        validate_clean(self)

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
    order = models.IntegerField(
        default=1,
        help_text='Defines the sort order in the parent row (lower numbers go first).',
    )

    # no need for a promote, search_desc is on content & slug isn't used
    promote_panels = [FieldPanel('order')]

    content_panels = Page.content_panels + [
        FieldPanel('link'),
        FieldPanel('search_description'),
        ImageChooserPanel('main_image'),
        SnippetChooserPanel('staff'),
    ]

    # redirect to external URL
    def serve(self, request):
        return redirect(self.link)
