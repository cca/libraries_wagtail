from django.test import TestCase
from api import get_instagram, linkify_text

# Create your tests here.
class LinkifyInstagramCaption(TestCase):

    def setUp(self):
        pass

    def username_test(self):
        """An Instagram caption with a username is properly linkified to HTML"""
        text = 'test @username'
        html = 'test <a href="https://www.instagram.com/username/">@username</a>'
        self.assertEqual(linkify_text(text), html)

    def hashtag_test(self):
        """An Instagram caption with a hashtag is properly linkified to HTML"""
        text = 'test #hashtag test'
        html = 'test <a href="https://www.instagram.com/explore/tags/hashtag">#hashtag</a> test'
        self.assertEqual(linkify_text(text), html)

    def hashtag_and_username_test(self):
        """An Instagram caption with both a hashtag _and_ a username is properly linkified to HTML"""
        text = 'test #hashtag and @username test'
        html = 'test <a href="https://www.instagram.com/explore/tags/hashtag">#hashtag</a> and <a href="https://www.instagram.com/username/">@username</a> test'
        self.assertEqual(linkify_text(text), html)
