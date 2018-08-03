from django.conf import settings
from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.core.models import Orderable, Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from categories.models import BaseStreamBlock

# Create your models here.

# Typical setup: Exhibits Index can only have Exhibit children,
# Exhibits can only have the Exhibits Index as a parent
class ExhibitsIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['exhibitions.ExhibitPage']

    # put list of all published exhibits in the page's context
    def get_context(self, request):
        exhibits = list(ExhibitPage.objects.live().order_by('-first_published_at'))
        context = super().get_context(request)
        context['exhibits'] = exhibits
        return context

    # allow only one instance of this page type
    @classmethod
    def can_create_at(cls, parent):
        return super(ExhibitsIndexPage, cls).can_create_at(parent) and not cls.objects.exists()

    front_matter = RichTextField(
        blank=True,
        features=settings.RICHTEXT_ADVANCED,
        help_text='Text that appears at the top of the index page by the title.'
    )

    epilogue = RichTextField(
        blank=True,
        features=settings.RICHTEXT_ADVANCED,
        help_text='Bottom text just above the footer (e.g. for licensing, attribution notes).'
    )

    content_panels = Page.content_panels + [
        FieldPanel('front_matter'),
        FieldPanel('epilogue'),
    ]


class ExhibitPage(Page):
    parent_page_types = ['exhibitions.ExhibitsIndexPage']
    subpage_types = [] # no children allowed

    display_choices = (
        ('banner', 'Single header image'),
        ('foursquare', 'Four square header images'),
    )
    display_template = models.CharField(
        choices=display_choices,
        default='banner',
        help_text='There are two layouts for the header; one large banner image or four square images set to the left of the title.',
        max_length=20,
    )

    # background color (do we still want this? doesn't seem useful…)

    location = RichTextField(
        blank=True,
        features=settings.RICHTEXT_BASIC,
        help_text='E.g. Simpson, Meyer',
    )
    dates = RichTextField(
        blank=True,
        features=settings.RICHTEXT_BASIC,
        help_text='Time period when the exibit ran.',
    )
    creators = RichTextField(
        blank=True,
        features=settings.RICHTEXT_BASIC,
        help_text='Name(s) of artists and curators.',
    )
    reception = RichTextField(
        blank=True,
        features=settings.RICHTEXT_BASIC,
        help_text='Details about the reception like date/time.',
    )
    description = StreamField(
        BaseStreamBlock(),
        verbose_name='Introduction/Description',
        null=True,
    )
    epilogue = RichTextField(
        blank=True,
        features=settings.RICHTEXT_ADVANCED,
        help_text='Footer text (e.g. for licensing, attribution)',
    )
    content_panels = Page.content_panels + [
        FieldPanel('display_template'),
        InlinePanel(
            'header_image',
            help_text='For the "Single header image" template only the first image is shown. For "Four square header images" all 4 images are shown in the order specified here.',
            label='Header Image',
            min_num=1,
            max_num=4,
        ),

        FieldPanel('location'),
        FieldPanel('dates'),
        FieldPanel('creators'),
        FieldPanel('reception'),

        StreamFieldPanel('description'),

        InlinePanel('exhibit_artwork', label='Exhibit pieces'),

        FieldPanel('epilogue'),
    ]

    # index related ExhibitArtworks
    search_fields = Page.search_fields + [
        index.RelatedFields('exhibit_artwork', [
            index.SearchField('title'),
            index.SearchField('creator'),
            index.SearchField('description'),
            index.SearchField('link'),
        ]),
    ]


class HeaderImage(Orderable):
    page = ParentalKey(ExhibitPage, related_name='header_image')

    image = models.ForeignKey(
        'wagtailimages.Image',
        help_text='Header image',
        null=False,
        blank=False,
            on_delete=models.CASCADE,
        related_name='+'
    )

    panels = [
        ImageChooserPanel('image'),
    ]

# represents one piece of media/art work for display in the gallery
class ExhibitArtwork(Orderable):
    page = ParentalKey(ExhibitPage, related_name='exhibit_artwork')

    type_choices = (
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('html', 'Embed code (HTML)'),
    )
    type = models.CharField(
        choices=type_choices,
        default='image',
        help_text='Used to determines the way this work appears in the gallery.',
        max_length=20,
    )

    title = models.CharField(blank=False, max_length=255)
    creator = models.TextField(blank=True, verbose_name="Creator(s)")
    link = models.TextField(
        blank=True,
        help_text='Optional, if provided the title will be hyperlinked to this URL.',
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        help_text='Image (used as the thumbnail if this isn\'t an "image" type work)',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+'
    )
    embed_code = models.TextField(
        blank=True,
        help_text='Optional, use this for HTML embeds, videos, audio, etc.',
    )
    description = RichTextField(
        blank=True,
        features=settings.RICHTEXT_BASIC,
        help_text='Notes or a general description.',
    )

    panels = [
        FieldPanel('type'),
        FieldPanel('title'),
        FieldPanel('creator'),
        FieldPanel('link'),
        ImageChooserPanel('image'),
        FieldPanel('embed_code'),
        FieldPanel('description'),
    ]
