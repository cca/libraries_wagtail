from unittest import TestCase

from django.core.exceptions import ValidationError

from instagram.api import get_instagram, linkify_text


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
        text = "test http://instagram.com"
        html = 'test <a href="http://instagram.com">http://instagram.com</a>'
        self.assertEqual(linkify_text(text), html)
        text = "http://instagram.com/path/to/file.jpg"
        html = '<a href="http://instagram.com/path/to/file.jpg">http://instagram.com/path/to/file.jpg</a>'
        self.assertEqual(linkify_text(text), html)

    def test_usename_and_url(self):
        """An Instagram caption with both a hashtag _and_ a URL is properly linkified to HTML"""
        text = "#hashtag and https://instagram.com"
        html = '<a href="https://www.instagram.com/explore/tags/hashtag/">#hashtag</a> and <a href="https://instagram.com">https://instagram.com</a>'
        self.assertEqual(linkify_text(text), html)


class GetInstagramFromFeedApiResponse(TestCase):
    def test_feed_shape_from_instagram_json(self) -> None:
        """Feed-style API payloads are parsed into the normalized Instagram fields."""
        payload: dict[str, object] = {
            "user": {"username": "ccalibraries"},
            "items": [
                {
                    "id": "3945615337323927014_5783472195",
                    "code": "DbBpD6ZhpXm",
                    "display_uri": "https://instagram.com/image.jpg",
                    "thumbnail_url": "https://instagram.com/thumb.jpg",
                    "accessibility_caption": "A descriptive accessibility caption",
                    "caption": {
                        "text": "Daniel Ransom from @ccalibraries shares resources at #library"
                    },
                    "owner": {"username": "ccafinearts"},
                    "image_versions2": {
                        "candidates": [{"url": "https://instagram.com/fallback.jpg"}]
                    },
                }
            ],
        }

        parsed: dict[str, str] = get_instagram(payload)

        self.assertEqual(parsed["id"], "3945615337323927014_5783472195")
        self.assertEqual(parsed["username"], "ccalibraries")
        self.assertEqual(parsed["url"], "https://instagram.com/p/DbBpD6ZhpXm")
        self.assertIn("Daniel Ransom", parsed["text"])
        self.assertIn('href="https://www.instagram.com/ccalibraries/"', parsed["html"])
        self.assertTrue(parsed["image"].startswith("https://"))


class GetInstagramFromLegacyApiResponse(TestCase):
    def test_legacy_shape_parses_expected_fields(self) -> None:
        """Legacy web_profile_info payloads are parsed into normalized fields."""
        payload: dict[str, object] = {
            "data": {
                "user": {
                    "edge_owner_to_timeline_media": {
                        "edges": [
                            {
                                "node": {
                                    "id": "1234567890",
                                    "shortcode": "AbCdEf123",
                                    "display_url": "https://instagram.com/image.jpg",
                                    "thumbnail_src": "https://instagram.com/thumb.jpg",
                                    "accessibility_caption": "A descriptive caption",
                                    "owner": {"username": "ccalibraries"},
                                    "edge_media_to_caption": {
                                        "edges": [
                                            {
                                                "node": {
                                                    "text": "Hello @ccalibraries #library"
                                                }
                                            }
                                        ]
                                    },
                                }
                            }
                        ]
                    }
                }
            }
        }

        parsed: dict[str, str] = get_instagram(payload)

        self.assertEqual(parsed["id"], "1234567890")
        self.assertEqual(parsed["username"], "ccalibraries")
        self.assertEqual(parsed["image"], "https://instagram.com/image.jpg")
        self.assertEqual(parsed["thumbnail_url"], "https://instagram.com/thumb.jpg")
        self.assertEqual(parsed["url"], "https://instagram.com/p/AbCdEf123")
        self.assertEqual(parsed["accessibility_caption"], "A descriptive caption")
        self.assertIn('href="https://www.instagram.com/ccalibraries/"', parsed["html"])
        self.assertIn(
            'href="https://www.instagram.com/explore/tags/library/"', parsed["html"]
        )


class GetInstagramInvalidPayloads(TestCase):
    def test_empty_payload_raises_validation_error(self) -> None:
        """Completely empty payloads should fail with a clear validation error."""
        with self.assertRaises(ValidationError) as ctx:
            get_instagram({})

        self.assertIn("supported Instagram JSON properties", str(ctx.exception))

    def test_deleted_schema_fail_payload_raises_validation_error(self) -> None:
        """Fail-status payloads from deleted schemas should be rejected by parser."""
        payload: dict[str, str] = {
            "message": "Asset asset://laser.provider/ig_business_category_subvertical has been deleted. You cannot use this schema",
            "status": "fail",
        }

        with self.assertRaises(ValidationError) as ctx:
            get_instagram(payload)

        self.assertIn("supported Instagram JSON properties", str(ctx.exception))
