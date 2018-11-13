import logging

from django.core.management.base import BaseCommand, CommandError
from instagram.api import get_instagram
from instagram.models import Instagram
from django.conf import settings

logger = logging.getLogger('mgmt_cmd.script')


class Command(BaseCommand):
    help = 'pulls latest @ccalibraries instagram post'

    def handle(self, *args, **options):
        if not hasattr(settings, 'INSTAGRAM_ACCESS_TOKEN'):
            logger.error('No INSTAGRAM_ACCESS_TOKEN in settings, exiting.')
            exit(1)
        else:
            # returns dict in form { html, image, text, username }
            insta = get_instagram()

            if 'html' in insta:
                # new Instagram from API response
                Instagram.objects.create(
                    text=insta['text'],
                    html=insta['html'],
                    image=insta['image'],
                    username=insta['username'],
                )

                self.stdout.write(self.style.SUCCESS('Latest Instagram retrieved successfully:'))
                self.stdout.write(insta['text'])

            else:
                logger.error('Unable to retrieved latest Instagram. IG Error Type: ""%s". Message: "%s"' % (insta['error_type'], insta['error_message']))
