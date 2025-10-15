import logging

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page, PreviewableMixin
from wagtail.search import index
from wagtail.snippets.models import register_snippet

logger = logging.getLogger(__name__)


# model for library staff
@register_snippet
class StaffMember(PreviewableMixin, models.Model):
    name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(default="username@cca.edu")
    phone = models.CharField(
        max_length=12,
        blank=True,
        default="415.703.5555",
        help_text='In form "555.555.5555"',
    )
    position = models.CharField(max_length=150)
    main_image = models.ForeignKey(
        "wagtailimages.Image",
        help_text="Use a roughly square image; it will be sized 150-by-150px on the staff list page.",
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    bio = RichTextField(
        features=settings.RICHTEXT_BASIC, help_text="A single 4-5 sentence paragraph."
    )
    revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="staff_member"
    )
    slug = models.CharField(max_length=150)

    panels = [
        FieldPanel("name", classname="title"),
        MultiFieldPanel(
            [
                FieldPanel("email", classname="col6"),
                FieldPanel("phone", classname="col6"),
                FieldPanel("position"),
            ]
        ),
        FieldPanel("main_image"),
        FieldPanel("bio"),
    ]

    def get_preview_context(self, request, mode_name):
        ctx = super().get_preview_context(request, mode_name)
        ctx["staff_member"] = {"staff_member": self}
        return ctx

    def get_preview_template(self, request, mode_name):
        return "staff/staff_member.html"

    # on save generate slug from email address
    def save(self, *args, **kwargs):
        self.slug = self.email.replace("@cca.edu", "")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# connection between staff & the staff page
class StaffPageStaffMembers(Orderable):
    page = ParentalKey("staff.StaffListPage", related_name="staff_members")
    staff_member = models.ForeignKey(
        "StaffMember", related_name="+", on_delete=models.CASCADE
    )

    panels = [
        FieldPanel("staff_member"),
    ]


# actual staff list page
class StaffListPage(Page, index.Indexed):
    parent_page_types = ["categories.RowComponent"]
    subpage_types = []
    max_count = 1

    main_image = models.ForeignKey(
        "wagtailimages.Image",
        help_text="Doesn't display on the page itself but a thumbnail close to 230x115px is used on the 'About Us' page and a smaller thumbnail is also used in search results.",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    post_script = RichTextField(
        features=settings.RICHTEXT_BASIC,
        blank=True,
        help_text="Text appears below the list of staff.",
    )
    order = models.IntegerField(
        default=1,
        help_text="Defines the sort order in the parent row (lower numbers go first).",
    )

    content_panels = Page.content_panels + [
        FieldPanel("main_image"),
        InlinePanel("staff_members", label="Staff Member"),
        FieldPanel("post_script"),
    ]
    promote_panels = Page.promote_panels + [FieldPanel("order")]

    # shouldn't have to do this hacky workaround but index.RelatedFields chokes
    # on the related StaffMember fields
    def get_related_staff_for_search(self):
        staff_fields = []

        for staff in self.staff_members.all():
            staff_fields.append(staff.staff_member.name)
            staff_fields.append(staff.staff_member.email)
            staff_fields.append(staff.staff_member.phone)
            staff_fields.append(staff.staff_member.position)
            staff_fields.append(staff.staff_member.bio)

        return "\n".join(staff_fields)

    search_fields = Page.search_fields + [
        index.AutocompleteField("get_related_staff_for_search")
    ]

    class Meta:
        ordering = ["order", "-last_published_at"]

    # for consistency with other child pages in categories app
    def category(self):
        return "about-us"

    # allow only one instance of the staff list page to be created
    @classmethod
    def can_create_at(cls, parent):
        return (
            super(StaffListPage, cls).can_create_at(parent) and not cls.objects.exists()
        )
