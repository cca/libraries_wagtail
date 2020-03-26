import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests

from instagram.api import get_token_from_code

logger = logging.getLogger('mgmt_cmd.script')


class Command(BaseCommand):
    help = "this will open an approval in a browser, then take you to a redirect URI with a 'code' parameter in the URL. It will use that code to obtain a shortlived access token and then exchange that in turn for a longlived access token."

    def handle(self, *args, **options):
        if (not hasattr(settings, 'INSTAGRAM_APP_ID') or
            not hasattr(settings, 'INSTAGRAM_APP_SECRET') or
            not hasattr(settings, 'INSTAGRAM_REDIRECT_URI')):
            logger.error('Need INSTAGRAM_APP_ID, INSTAGRAM_APP_SECRET, & INSTAGRAM_REDIRECT_URI in settings.')
            exit(1)
        else:
            self.stdout.write('Visit https://api.instagram.com/oauth/authorize?client_id={}&redirect_uri={}&scope=user_profile,user_media&response_type=code in a web browser, accept the prompt, then copy the code out of the URL that you are redirected to.'.format(settings.INSTAGRAM_APP_ID, settings.INSTAGRAM_REDIRECT_URI))
            code = input('Response code (do not include "#_" at end):')
            if get_token_from_code(code):
                logger.info('Added a new Instagram access token.')
            else:
                logger.info('Failed to acquire Instagram access token.')
                exit(1)
