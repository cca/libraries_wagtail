from django.conf import settings
from django.db import models
from libraries.utils import validate_clean
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index

from categories.models.pages import get_category


# Another child of RowComponent but with a very different structure & template
class SpecialCollectionsPage(Page):
    page_description = (
        "List page (of places, collections, etc.) with an image for each item."
    )
    parent_page_types = [
        "categories.RowComponent",
        "categories.ServicePage",
        "categories.AboutUsPage",
        "categories.SpecialCollectionsPage",
    ]
    subpage_types = [
        "categories.ServicePage",
        "categories.AboutUsPage",
        "categories.SpecialCollectionsPage",
    ]

    order = models.IntegerField(
        default=1,
        help_text="Defines the sort order in the parent row (lower numbers go first).",
    )

    # needs an orderable struct of some sort which contains a title, richtext
    # blurb, link to the external collection, and feature image _at least_
    content_panels = Page.content_panels + [
        InlinePanel("special_collections", label="Special Collection")
    ]
    promote_panels = Page.promote_panels + [FieldPanel("order")]

    # for search results—treat first SpecialCollection image as the page's image
    @property
    def main_image(self):
        return self.specific.special_collections.first().image

    def category(self):
        return get_category(self)

    def clean(self):
        super().clean()
        validate_clean(self)

    # make page searchable by text of child special collections
    search_fields = Page.search_fields + [
        index.RelatedFields(
            "special_collections",
            [
                index.AutocompleteField("title"),
                index.AutocompleteField("blurb"),
            ],
        ),
    ]


class SpecialCollection(Orderable):
    page = ParentalKey(SpecialCollectionsPage, related_name="special_collections")
    title = models.CharField(max_length=255)
    blurb = RichTextField(features=settings.RICHTEXT_BASIC)
    # URLField lets this link be either internal or external
    # Per Teri on 2017-08-09: some Spaces on a SpecColl page have no links
    link = models.URLField(blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        help_text="Close to a 2.25-by-1 aspect ratio is bst, image is sized to 910x400px at its largest.",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("blurb"),
        FieldPanel("link"),
        FieldPanel("image"),
    ]
