from unittest import TestCase

from instagram.api import linkify_text


class LinkifyInstagramCaption(TestCase):
    def test_username(self):
        """An Instagram caption with a username is properly linkified to HTML"""
        text = "test @username"
        html = 'test <a href="https://www.instagram.com/username/">@username</a>'
        self.assertEqual(linkify_text(text), html)

    def test_hashtag(self):
        """An Instagram caption with a hashtag is properly linkified to HTML"""
        text = "test #hashtag test"
        html = 'test <a href="https://www.instagram.com/explore/tags/hashtag/">#hashtag</a> test'
        self.assertEqual(linkify_text(text), html)

    def test_hashtag_and_username(self):
        """An Instagram caption with both a hashtag _and_ a username is properly linkified to HTML"""
        text = "test #hashtag and @username test"
        html = 'test <a href="https://www.instagram.com/explore/tags/hashtag/">#hashtag</a> and <a href="https://www.instagram.com/username/">@username</a> test'
        self.assertEqual(linkify_text(text), html)

    def test_url(self):
        """An Instagram caption with a URL is properly linkified to HTML"""
        text = "test http://example.com"
        html = 'test <a href="http://example.com">http://example.com</a>'
        self.assertEqual(linkify_text(text), html)
        text = "http://example.com/path/to/file.jpg"
        html = '<a href="http://example.com/path/to/file.jpg">http://example.com/path/to/file.jpg</a>'
        self.assertEqual(linkify_text(text), html)

    def test_usename_and_url(self):
        """An Instagram caption with both a hashtag _and_ a URL is properly linkified to HTML"""
        text = "#hashtag and https://example.com"
        html = '<a href="https://www.instagram.com/explore/tags/hashtag/">#hashtag</a> and <a href="https://example.com">https://example.com</a>'
        self.assertEqual(linkify_text(text), html)
