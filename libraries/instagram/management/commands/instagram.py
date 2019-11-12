import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from instagram.api import get_instagram
from instagram.models import Instagram, InstagramOAuthToken

logger = logging.getLogger('mgmt_cmd.script')


class Command(BaseCommand):
    help = 'pulls the latest Instagram post. Meant to run as a scheduled job.'

    def handle(self, *args, **options):
        if len(InstagramOAuthToken.objects.all()) == 0:
            logger.error('No Instagram OAuth tokens in database, run `python manage.py get_oauth_token` and follow the instructions to add one.')
            exit(1)
        else:
            # returns dict in form { html, image, text, username }
            insta = get_instagram()

            # did we get an error?
            if insta.get('error_type') is not None:
                logger.critical('Unable to retrieved latest Instagram. IG Error Type: "{0}". Message: "{1}"'.format(insta['error_type'], insta['error_message']))

            # do we already have this one?
            elif len(Instagram.objects.filter(ig_id=insta['id'])) > 0:
                logger.info('No new Instagram posts; we already have the most recent one.')
                exit(0)

            elif 'html' in insta:
                # new Instagram from API response
                Instagram.objects.create(
                    text=insta['text'],
                    html=insta['html'],
                    ig_id=insta['id'],
                    image=insta['image'],
                    username=insta['username'],
                )

                logger.info('Latest Instagram retrieved successfully: "{0}"'.format(insta['text']))

            else:
                logger.critical('Unable to retrieved latest Instagram. IG Error Type: "{0}". Message: "{1}"'.format(insta['error_type'], insta['error_message']))
