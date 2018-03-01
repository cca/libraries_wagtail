import os
import csv
import datetime
import sys
from io import BytesIO
import requests

from django.core.management.base import BaseCommand, CommandError
from django.core.files.images import ImageFile
from django.utils.html import strip_tags

from wagtail.images.models import Image

from blog.models import BlogIndex, BlogPage


def truncate(content, length=200, suffix='...'):
    if len(content) <= length:
        return content
    else:
        # split on spaces & drop the last entry, add suffix
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix


# NOTE: this creates duplicate images, see bug #39
# it'd be better to store in memory each created image, check for dupes on path
# and also make it reversible by deleting all created images/posts on error
def add_img_to_wagtail(path):
    root = 'http://libraries.cca.edu/'
    # our query returns a file path, not a URL, so there can be spaces
    img_url = root + path.replace(' ', '%20')
    filename = path.split('/')[-1]
    # Creating image object from URL based off of this gist:
    # https://gist.github.com/eyesee1/1ea8e1b90bfe632cd31f5a90afc0370c
    response = requests.get(img_url)
    image = Image.objects.create(
        title=filename,
        file=ImageFile(BytesIO(response.content), name=filename)),

    # for some reason .create() returns a tuple?
    # we want to return The Thing Itself instead, unencased
    return image[0]


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
        parser.add_argument(
            '-n', '--noimages',
            action='store_true',
            help='Do not download and create associated images',
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
                    # create a BlogPage from CSV data
                    try:
                        # date_created is a UNIX timestamp stored as a string
                        post_date = datetime.datetime.fromtimestamp(int(row['date_created']))
                        # strip HTML tags & truncate the body to create search description
                        search_desc = truncate(strip_tags(row['body']))
                        post = BlogPage(
                            title = row['title'],
                            slug = row['slug'],
                            search_description = search_desc,
                            date = post_date,
                            imported_body = row['body'],
                        )
                        # have to add this way to get page's depth & path fields right
                        blog_index.add_child(instance=post)
                        self.stdout.write(self.style.SUCCESS('Successfully created blog post %s' % post))
                    except:
                        self.stdout.write(self.style.ERROR('Unable to create blog post %s' % row['title']))
                        self.stdout.write(sys.exc_info()[0])

                    # if there is one, create an image in Wagtail & attach it to the blog post
                    img_field = row.get('main_image', None)

                    if not options['noimages'] and img_field and img_field != 'NULL':
                        try:
                            wagtail_image = add_img_to_wagtail(img_field)
                            post.main_image = wagtail_image
                            post.save()
                            self.stdout.write(self.style.SUCCESS( 'Successfully added main image %s' % img_field ))
                        except:
                            self.stdout.write(self.style.ERROR( 'Unable to add main image %s' % img_field ))
                            self.stdout.write(sys.exc_info()[0])
