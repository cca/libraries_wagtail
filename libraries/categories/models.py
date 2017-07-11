from django.db import models

from wagtail.wagtailcore.models import Page
# from home.models import HomePage


class ServicesPage(Page):
    parent_page_types = ['home.HomePage']

    # allow only one instance of this page type
    @classmethod
    def can_create_at(cls, parent):
        return super(ServicesPage, cls).can_create_at(parent) and not cls.objects.exists()


class CollectionsPage(Page):
    parent_page_types = ['home.HomePage']

    # allow only one instance of this page type
    @classmethod
    def can_create_at(cls, parent):
        return super(CollectionsPage, cls).can_create_at(parent) and not cls.objects.exists()


class AboutUsPage(Page):
    parent_page_types = ['home.HomePage']

    # allow only one instance of this page type
    @classmethod
    def can_create_at(cls, parent):
        return super(AboutUsPage, cls).can_create_at(parent) and not cls.objects.exists()
