import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from instagram.models import InstagramOAuthToken

logger = logging.getLogger('mgmt_cmd.script')


class Command(BaseCommand):
    help = "this will open an approval in a browser, then take you to a redirect URI with an 'access_token' parameter in the URL."

    def handle(self, *args, **options):
        if (not hasattr(settings, 'INSTAGRAM_CLIENT_ID') or
            not hasattr(settings, 'INSTAGRAM_REDIRECT_URI')):
            logger.error('Need both an INSTAGRAM_CLIENT_ID & INSTAGRAM_REDIRECT_URI in settings.')
            exit(1)
        else:
            self.stdout.write('Visit https://api.instagram.com/oauth/authorize/?client_id={}&redirect_uri={}&response_type=token in a web browser, accept the prompt, then copy the OAuth token out of the URL that you are redirected to.'.format(settings.INSTAGRAM_CLIENT_ID, settings.INSTAGRAM_REDIRECT_URI))
            token = input('OAuth token:')

            if len(token) > 0:
                InstagramOAuthToken.objects.create(
                    token=token,
                )
                logger.info('Added a new Instagram OAuth token.')
            else:
                self.stdout.write('No Instagram OAuth token was provided.')
