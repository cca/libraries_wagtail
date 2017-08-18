import os
import csv
import datetime
import sys
from urllib.request import urlretrieve

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from wagtail.wagtailredirects import models

from blog.models import BlogIndex, BlogPage


def download_img(path):
    root = 'http://libraries.cca.edu/'
    img_url = root + path.replace(' ', '%20')
    img_filename = path.split('/')[-1]
    dest = settings.BASE_DIR + '/media/' + img_filename
    urlretrieve(img_url, dest)


class Command(BaseCommand):
    help = 'import blog posts from a file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            nargs=1,
            help='pipe (|) separated blog posts with columns: title, slug, date_created, body, main_image',
        )
        parser.add_argument(
            '-d', '--dryrun',
            action='store_true',
            help='Print out blogs that would be created without creating them.',
        )

    def handle(self, *args, **options):
        filename = options['file'][0]
        blog_index = BlogIndex.objects.all().first()

        if not os.path.isfile(filename):
            raise CommandError('Could not find file at path "%s"' % filename)

        if options['dryrun']:
            self.stdout.write('Dry run, no database inserts. Parsed CSV data:')

        with open(filename) as f:
            # csv reader apparently too stupid to handle commas in fields so use "|"
            csvreader = csv.DictReader(f, delimiter='|')
            for row in csvreader:
                if options['dryrun']:
                    print(row)

                else:
                    # @TODO create new WagtailImage so we can link BlogPage to it?
                    img = row.get('main_image', None)

                    if img and img != 'NULL':
                        try:
                            download_img(img)
                            self.stdout.write(self.style.SUCCESS( 'Successfully downloaded %s' % img ))
                        except:
                            self.stdout.write(self.style.ERROR( 'Unable to download %s' % img ))
                            self.stdout.write(sys.exc_info()[0])

                    # create a BlogPage from CSV data
                    try:
                        # date_created is a UNIX timestamp stored as a string
                        post_date = datetime.datetime.fromtimestamp(int(row['date_created']))
                        post = BlogPage(
                            title = row['title'],
                            slug = row['slug'],
                            date = post_date,
                            imported_body = row['body'],
                        )
                        # have to add this way to get page's depth & path fields right
                        blog_index.add_child(instance=post)
                        self.stdout.write(self.style.SUCCESS('Successfully created blog post %s' % post ))
                    except:
                        self.stdout.write(self.style.ERROR('Unable to create blog post %s' % row['title']))
                        self.stdout.write(sys.exc_info()[0])
