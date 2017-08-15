import os
import csv

from django.core.management.base import BaseCommand, CommandError

from wagtail.wagtailredirects import models

from blog.models import BlogPage


class Command(BaseCommand):
    help = 'import blog posts from a file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            nargs=1,
            help='tab-separated blog posts with columns: title, slug, date_created, body, main image',
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

        # open file with newline='' to work around newlines in CSV fields
        with open(filename, 'r', newline='') as f:
            csvreader = csv.DictReader(f)
            for row in csvreader:
                if options['dryrun']:
                    print('Dry run - no database inserts. Here is the parsed blog export CSV:')
                    print(row)
                else:
                    # @TODO download image, create new WagtailImage?
                    BlogPage.objects.create(
                        title = row['title'],
                        slug = row['slug'],
                        date = int(row['date_created']),
                        date_created = int(row['date_created']),
                        imported_body = row['body'],
                    )
