import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Page

logger = logging.getLogger("mgmt_cmd.script")


class Command(BaseCommand):
    help = "Change the owner of pages owned by the ET Admin user."

    def add_arguments(self, parser):
        parser.add_argument(
            "username", nargs="?", type=str, help="username of new owner"
        )

    def handle(self, *args, **options):
        User = get_user_model()
        etadmin = User.objects.get(username="etadmin")
        if options["username"]:
            new_owner = User.objects.get(username=options["username"])
        else:
            new_owner = User.objects.get(username="ephetteplace")
        pages = Page.objects.filter(owner=etadmin).update(owner=new_owner)
