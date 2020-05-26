from datetime import datetime, timedelta
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from instagram.api import get_instagram, refresh_token
from instagram.models import Instagram, InstagramOAuthToken

logger = logging.getLogger('mgmt_cmd.script')


class Command(BaseCommand):
    help = 'pulls the latest Instagram post. Meant to run as a scheduled job.'

    def handle(self, *args, **options):
        if len(InstagramOAuthToken.objects.all()) == 0:
            logger.error('No Instagram OAuth tokens in database, run `python manage.py get_oauth_token` and follow the instructions to add one.')
            exit(1)
        else:
            otoken = InstagramOAuthToken.objects.last()
            # if the long-lived access token (lasts 60 days) is within 3 days of expiring, refresh it
            # DB is timezone-aware while now() is naive so need to normalize them
            if datetime.now() - otoken.date_added.replace(tzinfo=None) > timedelta(57, 0, 0):
                logger.info('Instagram OAuth token is 57 days old, refreshing it...')
                refresh_token(otoken.token)

            # returns dict in form { html, image, text, username }
            insta = get_instagram()

            # did we get an error?
            if insta.get('error_type') is not None:
                logger.critical('Unable to retrieved latest Instagram. IG Error Type: "{0}". Message: "{1}"'.format(insta['error_type'], insta['error_message']))
                exit(1)

            # do we already have this one?
            elif len(Instagram.objects.filter(ig_id=insta['id'])) > 0:
                logger.info('No new Instagram posts; we already have the most recent one.')
                exit(0)

            # new Instagram from API response
            Instagram.objects.create(
                text=insta['text'],
                html=insta['html'],
                ig_id=insta['id'],
                image=insta['image'],
                username=insta['username'],
            )
            logger.info('Latest Instagram retrieved successfully: "{0}"'.format(insta['text']))
