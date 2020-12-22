from unittest import TestCase
import requests

# Create your tests here.
class TestBrokenLink(TestCase):

    def test_post_broken_link(self):
        """POST data to the brokenlinks app (local server must be running)"""
        data = {
            'ipaddress': '127.0.0.1',
            'openurl': 'http://example.com/?super=long&query=string',
            'permalink': 'http://example.com/1234',
            'type': 'article',
            'email': 'me@me.com',
            'comments': 'help me please'
        }
        r = requests.post('http://127.0.0.1:8000/brokenlinks/', data=data)
        self.assertEqual(r.status_code, 200)
