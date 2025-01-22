import json
import logging
import re
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

# these functions are used inside management scripts exclusively
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


def get_instagram(insta: dict[str, Any]) -> dict[str, str]:
    """Parse Instagram API for the data we're interested in"""
    if "data" in insta:
        media: dict[str, Any] = (
            insta.get("data", {})
            .get("user", {})
            .get("edge_owner_to_timeline_media", {})
        )
        if len(media.get("edges", [])) == 0:
            raise ValueError("Unable to find posts in Instagram JSON data.")
        gram = media["edges"][0]["node"]
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

    else:
        raise ValidationError("Could not find data property in Instagram JSON.")
