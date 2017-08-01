from django.core.management.base import BaseCommand, CommandError
from instagram.api import get_instagram
from instagram.models import Instagram


class Command(BaseCommand):
    help = 'pulls latest @ccalibraries instagram post'

    def handle(self, *args, **options):
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
