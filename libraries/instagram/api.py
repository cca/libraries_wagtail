import json
import re
import requests
from django.conf import settings

# @me -> <a href=link>@me</a> etc.
def linkify_text(text):
    html = text
    username_regex = r"(^|\s)(@[a-zA-Z0-9._]+)"
    hashtag_regex = r"(^|\s)(#[a-zA-Z0-9]+)"
    ig_url = 'https://www.instagram.com/'


    def replace_username(match):
        leading_space = match.group(1)
        username = match.group(2).replace('@', '')
        return leading_space + '<a href="' + ig_url + username + '/">@' + username + '</a>'


    def replace_hashtag(match):
        leading_space = match.group(1)
        hashtag = match.group(2).replace('#', '')
        return leading_space + '<a href="' + ig_url + 'explore/tags/' + hashtag + '/">#' + hashtag + '</a>'

    # re.sub(pattern, replacement, string)
    html = re.sub(username_regex, replace_username, html)
    html = re.sub(hashtag_regex, replace_hashtag, html)
    return html


def get_instagram():
    url = 'https://api.instagram.com/v1/users/self/media/recent?access_token=' + settings.INSTAGRAM_ACCESS_TOKEN
    response = requests.get(url)
    insta = json.loads(response.text)
    gram = insta['data'][0]
    text = gram['caption']['text']

    output = {
        # link hashtags & usernames as they'd appear on IG itself
        'html': linkify_text(text),
        'image': gram['images']['low_resolution']['url'],
        'text': text,
        # we should already know this but just for ease of use
        'username': gram['user']['username'],
    }
    return output
