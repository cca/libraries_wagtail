from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page


class HomePage(Page):
    # background_image = models.ForeignKey('wagtailimages.Image', ...)
    # background_caption = RichTextField(blank=True)

    # @TODO the blurbs for the 3 main sections (services, collections, about us)
    # should be data represented in this model

    subpage_types = ['categories.ServicesPage', 'categories.CollectionsPage', 'categories.AboutUsPage']

    # don't allow more home pages to be created
    parent_page_types = []
    pass
