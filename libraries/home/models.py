from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel


class HomePage(Page):
    # background_image = models.ForeignKey('wagtailimages.Image', ...)
    # background_caption = RichTextField(blank=True)

    # blurbs for the 3 main sections (services, collections, about us)
    # we limit length & do not allow links like in a RichTextField
    latin = 'Aliquam iaculis ornare tristique. Phasellus ullamcorper tristique est, ac dictum quam sagittis ut.'
    services_text = models.CharField(default=latin, max_length=150)
    collections_text = models.CharField(default=latin, max_length=150)
    about_us_text = models.CharField(default=latin, max_length=150)

    subpage_types = ['categories.ServicesPage', 'categories.CollectionsPage', 'categories.AboutUsPage']

    # don't allow more home pages to be created
    parent_page_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('services_text'),
            FieldPanel('collections_text'),
            FieldPanel('about_us_text'),
        ], heading="Category Descriptions")
    ]
