import os

from django.core.management.base import BaseCommand, CommandError

from wagtail.wagtailredirects import models


class Command(BaseCommand):
    help = 'import blog posts from a file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            nargs=1,
            help='tab-separated blog posts with columns: title, slug, date, HTML body, image',
        )
        parser.add_argument(
            '-d', '--dryrun',
            action='store_true',
            help='Print out blogs that would be created without creating them.',
        )

    def handle(self, *args, **options):
        filename = options['file'][0]

        if not os.path.isfile(filename):
            raise CommandError('Could not find file at path "%s"' % filename)

        with open(filename) as f:
            lines = f.readlines()
            for line in lines:
                # this doesn't quite work, seems to choke onlines of a certain length
                (title, slug, date_created, date_changed, body, main_image) = line.split('\t')

                if options['dryrun']:
                    print(title, slug, date_created, body, main_image)
                else:
                    # create images
                    # create BlogPages
