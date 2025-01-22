from io import BytesIO
import json
import logging
from pathlib import Path
from typing import Any

import requests

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandError, CommandParser

from wagtail.models import Collection
from wagtail.images.models import Image

from instagram.api import get_instagram
from instagram.models import Instagram

logger = logging.getLogger("mgmt_cmd.script")


class Command(BaseCommand):
    help: str = "create an Instagram object from JSON"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--json",
            type=Path,
            required=True,
            help="Path to the Instagram JSON file to process",
        )
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        # Get JSON data from file path
        try:
            # Check if the file exists
            if not options["json"].exists():
                raise CommandError(f"File does not exist: {options['json']}")

            # Check if it's actually a file (not a directory)
            if not options["json"].is_file():
                raise CommandError(f"Path is not a file: {options['json']}")

            # Read and parse the JSON file
            with options["json"].open("r", encoding="utf-8") as file:
                try:
                    data: dict[str, Any] = json.load(file)
                except json.JSONDecodeError as e:
                    raise CommandError(f"Invalid JSON file: {str(e)}")

        except Exception as e:
            raise CommandError(f"An error occurred: {str(e)}")

        # Did we get an error in the JSON?
        if "error" in data:
            logger.critical(
                f'Unable to retrieve latest Instagram. Error: {data["error"]}'
            )
            exit(1)

        # get_instagram returns dict of just the data we're interested in
        insta: dict[str, str] = get_instagram(data)

        # do we already have this one?
        if len(Instagram.objects.filter(ig_id=insta["id"])) > 0:
            logger.info("No new Instagram posts; we already have the most recent one.")
            exit(0)

        # Add the image to Instagram collection in Wagtail
        # Videos have a thumbnail_url we use instead of media_url, images do not
        if insta["image"] != "":
            response: requests.Response = requests.get(insta["image"])
        elif insta["thumbnail_url"] != "":
            response: requests.Response = requests.get(insta["thumbnail_url"])
        else:
            raise CommandError(
                f"Neither image nor thumbnail_url present in Instagram data: {insta}"
            )

        collections = Collection.objects.filter(name="Instagram")
        if collections.exists():
            instagram_collection = collections[0]
        else:
            # "Root" collection
            instagram_collection = Collection.objects.filter(id=1)[0]

        try:
            image: Image | None = Image.objects.create(
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
