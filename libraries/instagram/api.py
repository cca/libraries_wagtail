import json
import logging
import re
import requests

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from wagtail.models import Site

from .models import InstagramSettings

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


def get_instagram() -> dict[str, str]:
    default_site = Site.objects.filter(is_default_site=True)[0]
    ig_settings = InstagramSettings.for_site(site=default_site)
    headers = {
        # this is internal ID of an instegram backend app. It doesn't change often.
        "x-ig-app-id": ig_settings.ig_app_id,
        # use browser-like features
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
    }
    response = requests.get(
        f"https://i.instagram.com/api/v1/users/web_profile_info/?username={ig_settings.instagram_account}",
        headers=headers,
    )
    try:
        response.raise_for_status()
    except:
        # TODO email site admins
        logger.error(
            f"Error retrieving Instagram data. Response: {response.status_code} {response.url}\nText: {response.text}"
        )
        return {
            "error_type": "HTTP Status Error",
            "error_message": response.text,
        }
    insta = response.json()

    if "data" in insta:
        gram = insta["data"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]
        # caption is ["edge_media_to_caption"]["edges"][0]["node"]["text"]
        # where edges is empty list if there is no caption
        # I did not see an example of multiple captions or a non-text node
        first_caption = ""
        if len(gram.get("edge_media_to_caption", {}).get("edges", [])):
            first_caption = (
                gram["edge_media_to_caption"]["edges"][0]
                .get("node", {})
                .get("text", "")
            )

        return {
            # AI-generated
            "accessibility_caption": gram.get("accessibility_caption", ""),
            # link hashtags & usernames as they'd appear on IG itself
            "html": linkify_text(first_caption),
            "id": gram.get("id", ""),
            "image": gram.get("display_url", ""),
            "raw_json": json.dumps(gram),
            "text": first_caption,
            # there's also gram["thumbnail_resources"] which is a list of {src,config_width,config_height} objects
            "thumbnail_url": gram.get("thumbnail_src", ""),
            "url": (
                f"https://instagram.com/p/{gram.get('shortcode')}"
                if gram.get("shortcode")
                else ""
            ),
            # should always be the same as ig_settings.instagram_account
            "username": gram.get("owner", {}).get("username", ""),
        }

    elif "error" in insta:
        return {
            "error_type": insta.get("error", {}).get("type", ""),
            "error_message": insta.get("error", {}).get("message", ""),
        }

    else:
        return {
            "error_type": "GenericError",
            "error_message": 'No "error" object containing an error type or message was present in the Instagram response but we also could not find the data we were looking for. This likely means a network connection problem or Instagram changed their data structure.',
        }
