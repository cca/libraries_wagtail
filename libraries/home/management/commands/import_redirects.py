import os

from django.core.management.base import BaseCommand, CommandError

from wagtail.contrib.redirects import models


# import redirect mgmt command
# but Eric, why does this belong in the home page app?
# Good question! Because the root "libraries" app apparently cannot hold mgmt
# commands (they don't get detected by manage.py) so I put it here.
class Command(BaseCommand):
    help = "import redirects from a file"

    def add_arguments(self, parser):
        parser.add_argument(
            "file",
            nargs=1,
            help="comma-separated file of paths & redirect destinations",
        )
        parser.add_argument(
            "-d",
            "--dryrun",
            action="store_true",
            help="Print out redirects that would be created without creating them.",
        )

    def handle(self, *args, **options):
        # expects a comma-separated file of format redirect_from_path,url_to_redirect_to
        # e.g. lines like /example,http://example.com
        filename = options["file"][0]

        if not os.path.isfile(filename):
            raise CommandError('Could not find file at path "%s"' % filename)

        with open(filename) as f:
            lines = f.readlines()
            for line in lines:
                old_path, redirect_link = line.rstrip("\n").split(",")

                # wagtail redirects should begin with "/" or they're useless
                if old_path[0] != "/":
                    old_path = "/" + old_path

                if options["dryrun"]:
                    print(old_path, redirect_link)
                else:
                    try:
                        models.Redirect.objects.create(
                            old_path=old_path,
                            redirect_link=redirect_link,
                        )
                        self.stdout.write(
                            self.style.SUCCESS("added redirect from %s to %s")
                            % (old_path, redirect_link)
                        )
                    except Exception as e:
                        self.stderr.write(
                            self.style.ERROR("unable to create redirect from %s to %s")
                            % (old_path, redirect_link)
                        )
