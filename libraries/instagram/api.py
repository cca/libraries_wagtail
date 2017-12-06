import json
import re
import requests
from django.conf import settings

# @me -> <a href=link>@me</a> etc.
def linkify_text(text):
    html = text
    username_regex = r"@[a-zA-Z0-9]+"
    hashtag_regex = r"#[a-zA-Z0-9]+"
    ig_url = 'https://www.instagram.com/'


    def replace_username(match):
        username = match.group(0).replace('@', '')
        return '<a href="' + ig_url + username + '/">@' + username + '</a>'


    def replace_hashtag(match):
        hashtag = match.group(0).replace('#', '')
        return '<a href="' + ig_url + 'explore/tags/' + hashtag + '/">#' + hashtag + '</a>'

    # re.sub(pattern, replacement, string)
    html = re.sub(username_regex, replace_username, html)
    html = re.sub(hashtag_regex, replace_hashtag, html)
    return html


def get_instagram():
    url = 'https://www.instagram.com/{u}/?__a=1'.format(u=settings.INSTAGRAM_USERNAME)
    response = requests.get(url)
    insta = json.loads(response.text)
    gram = insta['user']['media']['nodes'][0]
    text = gram['caption']

    output = {
        # link hashtags & usernames as they'd appear on IG itself
        'html': linkify_text(text),
        'image': gram['thumbnail_src'],
        'text': text,
        # we should already know this in a template but just for ease of use
        'username': settings.INSTAGRAM_USERNAME,
    }
    return output
