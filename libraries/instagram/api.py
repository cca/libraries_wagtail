import logging
import re
import requests

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import InstagramOAuthToken

# these functions will be used inside management scripts exclusively
logger = logging.getLogger("mgmt_cmd.script")
validate_url = URLValidator()


# @me -> <a href=link>@me</a> etc.
def linkify_text(text):
    html = text
    username_regex = r"(^|\s)(@[a-zA-Z0-9._]+)"
    hashtag_regex = r"(^|\s)(#[a-zA-Z0-9_]+)"
    url_regex = r"(^|\s)(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))"
    ig_url = "https://www.instagram.com/"

    def replace_username(match):
        leading_space = match.group(1)
        username = match.group(2).replace("@", "")
        return (
            leading_space + '<a href="' + ig_url + username + '/">@' + username + "</a>"
        )

    def replace_hashtag(match):
        leading_space = match.group(1)
        hashtag = match.group(2).replace("#", "")
        return (
            leading_space
            + '<a href="'
            + ig_url
            + "explore/tags/"
            + hashtag
            + '/">#'
            + hashtag
            + "</a>"
        )

    def replace_url(match):
        leading_space = match.group(1)
        url = match.group(2)
        try:
            validate_url(url)
        except ValidationError:
            logger.warning(
                'Regex found invalid URL "{}" in Instagram post.'.format(url)
            )
            # return unprocessed string
            return match.string
        return leading_space + '<a href="' + url + '">' + url + "</a>"

    html = re.sub(username_regex, replace_username, html)
    html = re.sub(hashtag_regex, replace_hashtag, html)
    html = re.sub(url_regex, replace_url, html)
    return html


def get_instagram():
    # just grab the latest OAuth token we have
    OAuthToken = InstagramOAuthToken.objects.last()
    if OAuthToken is None:
        return {
            "error_type": "NoOAuthToken",
            "error_message": "No Instagram OAuth token found in database. Run `python manage.py get_oauth_token` and follow the instructions to add one.",
        }
    token = OAuthToken.token
    url = (
        "https://graph.instagram.com/me/media?fields=id,caption,media_url,permalink,thumbnail_url,username&access_token="
        + token
    )
    response = requests.get(url)
    insta = response.json()

    if "data" in insta:
        gram = insta["data"][0]
        text = gram["caption"]

        output = {
            # link hashtags & usernames as they'd appear on IG itself
            "html": linkify_text(text),
            "id": gram["id"],
            "image": gram["media_url"],
            "text": text,
            "thumbnail_url": gram.get("thumbnail_url", None),
            "username": gram["username"],
        }

    elif "error" in insta:
        output = {
            "error_type": insta["error"]["type"],
            "error_message": insta["error"]["message"],
        }

    else:
        output = {
            "error_type": "GenericError",
            "error_message": 'No "error" object containing an error type or message was present in the Instagram API response. This likely means a network connection problem or that Instagram changed the structure of their error messages.',
        }

    return output


def get_token_from_code(code):
    """Turn a code from the app's redirect URI into a long-lived OAuth access token.

    Parameters
    ----------
    code : str
        the "code" parameter in the app's redirect URI

    Returns
    -------
    boolean
        True if token was successfully obtained, False if an error occurred.
    """
    if len(code) == 0:
        logger.info("No response code provided.")
        return False

    data = {
        "client_id": settings.INSTAGRAM_APP_ID,
        "client_secret": settings.INSTAGRAM_APP_SECRET,
        # strip the final two "#_" characters in case user included them
        "code": code.rstrip("#_"),
        "grant_type": "authorization_code",
        "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
    }
    logger.info("obtaining short-lived Instagram access token")
    response = requests.post("https://api.instagram.com/oauth/access_token", data=data)
    shortlived_token = response.json().get("access_token")
    if not shortlived_token:
        logger.error(
            "Failed to acquire shortlived access token. Response JSON: {}".format(
                response.json()
            )
        )
        return False

    # https://developers.facebook.com/docs/instagram-basic-display-api/reference/access_token
    # exchange this worthless shortlived token for a long-lived one
    # Facebook is GREAT at API design, by the way, really love their work
    logger.info("obtaining long-lived Instagram access token")
    ll_response = requests.get(
        "https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret={}&access_token={}".format(
            settings.INSTAGRAM_APP_SECRET, shortlived_token
        )
    )
    token = ll_response.json().get("access_token")

    if token:
        InstagramOAuthToken.objects.create(token=token)
        return True
    logger.error(
        "Failed to acquire long-lived OAuth token. Response JSON: {}".format(
            response.json()
        )
    )
    return False


def refresh_token(token):
    """refresh Instagram long-lived access token
    where the word "refresh" means "replace", it is not the same token"""
    response = requests.get(
        "https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token={}".format(
            token
        )
    )
    new_token = response.json().get("access_token")
    if new_token:
        InstagramOAuthToken.objects.create(token=new_token)
        logger.info("Successfully refreshed long-lived Instagram access token.")
        return new_token
    logger.critical(
        "Unable to refresh long-lived Instagram access token. Response JSON: {}".format(
            response.json()
        )
    )
    return None
