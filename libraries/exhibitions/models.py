from django.conf import settings
from django.db import models
from django.http import FileResponse

from modelcluster.fields import ParentalKey

from wagtail.core import hooks
from wagtail.core.models import Orderable, Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, HelpPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from categories.models import BaseStreamBlock

# logic for showing/hiding appropriate art work fields based on type
@hooks.register('insert_editor_js')
def editor_js():
    file = settings.STATIC_URL + 'js/exhibits-admin.js'
    return '<script src="{0}"></script>'.format(file)

# Typical setup: Exhibits Index can only have Exhibit children,
# Exhibits can only have the Exhibits Index as a parent
class ExhibitsIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['exhibitions.ExhibitPage']
    max_count = 1

    # put list of all published exhibits in the page's context
    def get_context(self, request):
        exhibits = list(ExhibitPage.objects.live().order_by('-first_published_at'))
        context = super().get_context(request)
        context['exhibits'] = exhibits
        return context


    class Meta:
        ordering = ["order", "-last_published_at"]

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
    order = models.IntegerField(
        default=1,
        help_text='Defines the sort order in the parent row (lower numbers go first).',
    )

    content_panels = Page.content_panels + [
        FieldPanel('front_matter'),
        FieldPanel('epilogue'),
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel('order')
    ]


class ExhibitPage(Page):
    parent_page_types = ['exhibitions.ExhibitsIndexPage']
    subpage_types = [] # no children allowed

    # theme choices
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
    gallery_columns = models.IntegerField(
        default=2,
        help_text='Recommended to be 2 or 3. Other numbers may cause odd layouts.'
    )
    gallery_spacing = models.IntegerField(
        default=4,
        help_text='Horizontal padding (in pixels) between works in the gallery.'
    )
    # offer CCA brand fonts where possible, monospace is only one we don't have
    font_choices = (
        ('serif', 'Default (The Serif/Merriweather)'),
        ('sans-serif', 'Sans Serif (Brown/Raleway)'),
        ('stencil', 'Stencil (Le Corbusier/Stardos Stencil)'),
        ('monospace', 'Monospace (Consolas)'),
    )
    main_body_font = models.CharField(
        choices=font_choices,
        default='serif',
        help_text='Font applied to the Description & other details (location/reception/etc.) below.',
        max_length=50
    )

    # details about exhibition
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
        verbose_name='Description',
        null=True,
    )
    epilogue = RichTextField(
        blank=True,
        features=settings.RICHTEXT_ADVANCED,
        help_text='Footer text (e.g. for licensing, attribution)',
    )
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('display_template'),
                InlinePanel(
                    'header_image',
                    help_text='For the "Single header image" template only the first image is shown. For "Four square header images" 4 images are shown in the order specified here.',
                    label='Header Image',
                    min_num=1,
                    max_num=4,
                ),
                FieldPanel('gallery_columns'),
                FieldPanel('gallery_spacing'),
                FieldPanel('main_body_font'),
            ],
            heading='Theme',
        ),

        MultiFieldPanel(
            [
                StreamFieldPanel('description'),
                FieldPanel('location'),
                FieldPanel('dates'),
                FieldPanel('creators'),
                FieldPanel('reception'),
            ],
            heading='Exhibition details',
        ),

        HelpPanel(
            content="""
<style scoped>
p { font-size: 1.2em; }
</style>
<p>
    Gallery images are restricted to a 630x630 space <em>with their aspect ratio retained</em> but their full size is visible in the fullscreen viewer. There's no reason to upload an image larger than 2,000 pixels since most screens will not be that large. The work's description also displays. If you provide a link URL, the title in the fullscreen viewer will be hyperlinked to it.
</p>
<p>
    For YouTube or Vimeo, select type <b>Embed code</b> and fill in the URL for the video (no need for <code>&lt;iframe&gt;</code> HTML). For other sources, you need <strong>only enter the URL contained in the code</strong>, usually as the "src" attribute of an <code>&lt;iframe&gt;</code> element. For these works, you may still specify an image; it will be used as the thumbnail. If you <em>don't</em> add an image and it's a YouTube embed, Wagtail grabs a 480x360 thumbnail from YouTube. However, it's strongly recommended to provide an image in these cases to avoid layout problems.
</p>
            """,
            heading='Information on Adding Artworks',
        ),

        InlinePanel('exhibit_artwork', label='Exhibit pieces'),

        FieldPanel('epilogue'),
    ]

    @property
    def column_width(self):
        """
        The maximum size of each gallery column based on the values for number
        of columns and spacing in between those columns (gutter).
        """
        # col width = width of container (1260) minus space taken up by gutters
        # (one fewer gutter than no. columns) divided by no. columns
        width = (1260 - (self.gallery_columns - 1) * self.gallery_spacing) / self.gallery_columns
        return width

    @property
    def contains_video(self):
        if len(self.exhibit_artwork.filter(type='video')) > 0:
            return True

        for code in [work.embed_code for work in self.exhibit_artwork.filter(type='html')]:
            if 'vimeo.com' in code or 'youtube.com' in code or 'youtu.be' in code:
                return True

        return False

    @property
    def contains_vimeo(self):
        for code in [work.embed_code for work in self.exhibit_artwork.filter(type='html')]:
            if 'vimeo.com' in code:
                return True

        return False

    # index related ExhibitArtworks
    search_fields = Page.search_fields + [
        index.SearchField('description'),
        index.SearchField('location'),
        index.SearchField('dates'),
        index.SearchField('reception'),
        index.SearchField('creators'),
        index.SearchField('epilogue'),
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
        help_text='Single header images should be ≥ 1360px wide; they will be strecthed if not. Foursquare images are sized to a 400x400 square but you can upload larger images.',
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
        related_name='+',
    )
    media = models.ForeignKey(
        'wagtaildocs.Document',
        help_text='Video or audio to embed. Only needed for video/audio types.',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    embed_code = models.TextField(
        blank=True,
        help_text='Also used for YouTube or Vimeo. Just copy the URL of the video e.g. https://www.youtube.com/watch?v=F1B9Fk_SgI0 and not the full <iframe> wrapped HTML.',
    )
    description = RichTextField(
        blank=True,
        features=settings.RICHTEXT_BASIC,
        help_text='Notes or a general description.',
    )

    panels = [
        FieldPanel('type', classname='js-type'),
        FieldPanel('title'),
        FieldPanel('creator'),
        FieldPanel('link'),
        ImageChooserPanel('image', classname='js-image'),
        DocumentChooserPanel('media', classname='js-media'),
        FieldPanel('embed_code', classname='js-embed_code'),
        FieldPanel('description'),
    ]


    def __str__(self):
        return self.title
