from io import BytesIO
import logging
import requests

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand

from wagtail.models import Collection
from wagtail.images.models import Image

from instagram.api import get_instagram
from instagram.models import Instagram

logger = logging.getLogger("mgmt_cmd.script")


class Command(BaseCommand):
    help = "pulls the latest Instagram post. Meant to run as a scheduled job."

    def handle(self, *args, **options):
        # returns dict in form { html, image, text, username } or { error_type, error_message }
        insta: dict[str, str] = get_instagram()

        # did we get an error?
        if "error_type" in insta:
            logger.critical(
                f'Unable to retrieve latest Instagram. Error Type: {insta["error_type"]}. Message: {insta["error_message"]}'
            )
            exit(1)

        # do we already have this one?
        elif len(Instagram.objects.filter(ig_id=insta["id"])) > 0:
            logger.info("No new Instagram posts; we already have the most recent one.")
            exit(0)

        # First add the image to Instagram collection in Wagtail
        # Videos have a thumbnail_url we use instead of media_url, images do not
        if insta["thumbnail_url"] is not None:
            response = requests.get(insta["thumbnail_url"])
        else:
            response = requests.get(insta["image"])

        collections = Collection.objects.filter(name="Instagram")
        if collections.exists():
            instagram_collection = collections[0]
        else:
            # "Root" collection
            instagram_collection = Collection.objects.filter(id=1)[0]

        try:
            image = Image.objects.create(
                title=(
                    f'Instagram Post {insta.get("url") if insta.get("url") else insta["id"]}'
                ),
                file=ImageFile(
                    BytesIO(response.content), name="{}.jpg".format(insta["id"])
                ),
                collection=instagram_collection,
            )
        except:
            logger.warning(
                "Unable to create Wagtail Image from Instagram URL: {}".format(
                    insta["image"]
                )
            )
            image = None

        # new Instagram from API response
        # We should have all these dict properties at least as empty strings, see api.get_instagram
        Instagram.objects.create(
            accessibility_caption=insta["accessibility_caption"],
            html=insta["html"],
            ig_id=insta["id"],
            image=image,
            image_url=insta["image"] if insta["image"] else insta["thumbnail_url"],
            json=insta["raw_json"],
            text=insta["text"],
            username=insta["username"],
        )
        logger.info(
            'Latest Instagram retrieved successfully: "{0}"'.format(insta["text"])
        )
