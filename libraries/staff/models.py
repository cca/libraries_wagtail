from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

# model for library staff
@register_snippet
class StaffMember(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=12, help_text='In form "555.555.5555"')
    position = models.CharField(max_length=150)
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    bio = RichTextField(help_text='A single 4-5 sentence paragraph.')

    panels = [
        FieldPanel('name'),
        MultiFieldPanel([
            FieldPanel('email'),
            FieldPanel('phone'),
            FieldPanel('position'),
        ]),
        ImageChooserPanel('main_image'),
        FieldPanel('bio'),
    ]

    def __str__(self):
        return self.name

# connection between staff & the staff page
class StaffPageStaffMembers(Orderable, StaffMember):
    page = ParentalKey('staff.StaffListPage', related_name='staff_members')

# actual staff list page
class StaffListPage(Page):
    parent_page_types = ['categories.RowComponent']
    subpage_types = []
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        help_text='Only used in search results right now',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel('main_image'),
        InlinePanel('staff_members', label='Staff Member'),
    ]

    search_fields = [
        index.RelatedFields('staff_members', [
            index.SearchField('name'),
            index.SearchField('email'),
            index.SearchField('phone'),
            index.SearchField('position'),
            index.SearchField('bio'),
        ]),
    ]

    # for consistency with other child pages in categories app
    def category(self):
        return 'about-us'

    # allow only one instance of the staff list page to be created
    def can_create_at(cls, parent):
        return super(StaffListPage, cls).can_create_at(parent) and not cls.objects.exists()
