from django.core.management.base import BaseCommand, CommandError
from instagram.api import get_instagram
from instagram.models import Instagram
from django.conf import settings


class Command(BaseCommand):
    help = 'pulls latest @ccalibraries instagram post'

    def handle(self, *args, **options):
        if not hasattr(settings, 'INSTAGRAM_ACCESS_TOKEN'):
            self.stderr.write(self.style.ERROR('Error: No INSTAGRAM_ACCESS_TOKEN in settings, exiting.'))
            exit(1)
        else:
            # returns dict in form { html, image, text, username }
            insta = get_instagram()

            Instagram.objects.create(
                text=insta['text'],
                html=insta['html'],
                image=insta['image'],
                username=insta['username'],
            )

            self.stdout.write(self.style.SUCCESS('Latest @ccalibraries Instagram retrieved successfully:'))
            self.stdout.write(insta['text'])
