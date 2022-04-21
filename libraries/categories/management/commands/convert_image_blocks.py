"""
One-time StreamField migration:
- ImageBlock -> LinkedImageBlock
- LinkedImageBlock -> Add PageChooserBlock so we can link to internal or external URLs
"""
import logging

from django.core.management.base import BaseCommand
from wagtail.core.blocks.stream_block import StreamValue

from blog.models import BlogPage
from categories.models import ServicePage
from exhibitions.models import ExhibitPage

logger = logging.getLogger('mgmt_cmd.script')


def convertImageBlock(block):
    # change the type & add null fields for external_url, page
    new_block = block
    new_block['type'] = 'linked_image'
    new_block['value']['external_url'] = None
    new_block['value']['page'] = None
    return new_block


def convertLinkedImageBlock(block):
    # move "link" field to external_url, add null page field
    new_block = block
    new_block['value']['external_url'] = new_block['value'].pop('link')
    new_block['value']['page'] =  None
    return new_block


def convertBlock(block):
    # convert Image/LinkedImage blocks, recurse into children within Row blocks
    if block['type'] == 'image':
        globals()['page_was_changed'] = True
        return convertImageBlock(block)
    if block['type'] == 'linked_image' and block['value'].get('link'):
        globals()['page_was_changed'] = True
        return convertLinkedImageBlock(block)
    elif block['type'] == 'row':
        new_row = block
        new_row['value'] = [convertBlock(subblock) for subblock in block['value']]
        return new_row
    else:
        return block


def convertBlocksOfModel(model, streamfield):
    logger.info('Converting all blocks for pages using the {} model.'.format(model))
    for page in model.objects.all():
        global page_was_changed
        page_was_changed = False
        new_stream_data = [convertBlock(block) for block in getattr(page, streamfield).raw_data]
        if page_was_changed:
            stream_block = getattr(page, streamfield).stream_block
            setattr(page, streamfield, StreamValue(stream_block, new_stream_data, is_lazy=True))
            page.save()
            logger.info("{} had Image or LinkedImage blocks which were converted.".format(page.title))


class Command(BaseCommand):
    help = 'converts ImageBlocks to LinkedImageBlocks, adds "page" field to LinkedImageBlocks'

    def handle(self, *args, **options):
        # these are all the models that use the BaseStreamBlock which includes
        # both ImageBlock and LinkedImageBlock
        convertBlocksOfModel(BlogPage, 'body')
        convertBlocksOfModel(ExhibitPage, 'description')
        convertBlocksOfModel(ServicePage, 'body')
