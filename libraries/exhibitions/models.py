from django.conf import settings
from django.db import models
from django.http import FileResponse

from modelcluster.fields import ParentalKey

from wagtail.core import hooks
from wagtail.core.models import Orderable, Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, HelpPanel, InlinePanel, StreamFieldPanel
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from categories.models import BaseStreamBlock

# logic for showing/hiding appropriate art work fields based on type
@hooks.register('insert_editor_js')
def editor_js():
    file = settings.STATIC_URL + 'js/exhibits-admin.js'
    return '<script src="{0}"></script>'.format(file)

# TODO: don't force all documents to be downloaded with HTTP header
# Content-Disposition: attachment (this doesn't work right now)
@hooks.register('before_serve_document')
def before_serve_document(document, request):
    if request.GET.get('nodownload', '') != '':
        response = FileResponse(document.file)
        del response['Content-Disposition']
        return response

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

        HelpPanel(content="""
<style scoped>
p { font-size: 1.2em; }
</style>
<p>
    Gallery images are restricted to a 600x600 space with their aspect ratio retained but their full size is visible in the fullscreen viewer. The work's description also displays. If you provide a link URL, the title in the fullscreen viewer will be hyperlinked to it.
</p>
<p>
    For embed codes, <em>only enter the URL</em> contained in the code, usually as the "src" attribute of an <code>&lt;iframe&gt;</code> element. You can still add an image to the work; it will be used as the thumbnail in the gallery. If you <em>don't</em> add an image and it's a YouTube embed, Wagtail grabs a 480x360 thumbnail from YouTube. For embeds from other sources, we can work on building specific handlers that do something similar. Right now, if you don't specify an image and it's not a YouTube URL, the iframe itself is shown. It's strongly recommended to provide an image in these cases to avoid weird layout problems.
</p>
        """, heading='Information on Adding Artworks'),

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
        help_text='Can be used for YouTube/Vimeo videos. ONLY PASTE THE EMBED URL e.g. https://youtube.com/embed/KbjGqRdPF7s and not the full <iframe> wrapped HTML.',
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
