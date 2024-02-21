from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Page, Site


class Command(BaseCommand):
    help = 'Print list of pages with no search_description field.'

    def handle(self, *args, **options):
        pages = Page.objects.live().filter(search_description='', depth__gte=2)
        for page in pages:
            print(page.title, Site.objects.first().hostname + page.url, page.owner)
