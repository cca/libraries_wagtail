import socket
import unittest
import warnings
from unittest import TestCase

import requests


# Create your tests here.
class TestBrokenLink(TestCase):
    @unittest.skip("Disabled: Summon broken link report form has been disabled")
    def test_post_broken_link(self) -> None:
        """POST data to the brokenlinks app (local server must be running)"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            is_running: bool = sock.connect_ex(("127.0.0.1", 8000)) == 0

        if not is_running:
            warnings.warn(
                "Skipping broken link POST test: local server is not running on 127.0.0.1:8000",
                RuntimeWarning,
            )
            self.skipTest("Local server is not running on 127.0.0.1:8000")

        data: dict[str, str] = {
            "ipaddress": "127.0.0.1",
            "openurl": "http://example.com/?super=long&query=string",
            "permalink": "http://example.com/1234",
            "type": "article",
            "email": "me@me.com",
            "comments": "help me please",
        }
        r = requests.post("http://127.0.0.1:8000/brokenlinks/", data=data, timeout=5)
        self.assertEqual(r.status_code, 200)
