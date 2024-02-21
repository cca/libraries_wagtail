# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-22 23:45
from __future__ import unicode_literals

import categories.models
from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0023_row_block_maximum'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aboutuspage',
            name='body',
            field=wagtail.fields.StreamField((('paragraph', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link', 'h3', 'ol', 'ul', 'image', 'embed', 'hr'], icon='pilcrow')),), null=True, verbose_name='Page content'),
        ),
        migrations.AlterField(
            model_name='servicepage',
            name='body',
            field=wagtail.fields.StreamField((('subheading', wagtail.blocks.CharBlock(classname='title', icon='title', template='categories/blocks/subheading.html')), ('paragraph', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link', 'h3', 'ol', 'ul', 'image', 'embed', 'hr'], icon='pilcrow', template='categories/blocks/paragraph.html')), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link'], required=False))))), ('linked_image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link'], required=False)), ('link', wagtail.blocks.URLBlock())))), ('pullquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('name', wagtail.blocks.CharBlock(required=False)), ('position', wagtail.blocks.CharBlock(label='Position or affiliation', required=False))))), ('snippet', wagtail.blocks.RichTextBlock(label='Callout', template='categories/blocks/snippet.html')), ('html', categories.models.EmbedHTML(label='Embed code')), ('row', wagtail.blocks.StreamBlock((('paragraph', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link', 'h3', 'ol', 'ul', 'image', 'embed', 'hr'], icon='pilcrow', template='categories/blocks/paragraph.html')), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link'], required=False))))), ('linked_image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link'], required=False)), ('link', wagtail.blocks.URLBlock())))), ('pullquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('name', wagtail.blocks.CharBlock(required=False)), ('position', wagtail.blocks.CharBlock(label='Position or affiliation', required=False))))), ('snippet', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link', 'h3', 'ol', 'ul', 'image', 'embed', 'hr'], label='Callout', template='categories/blocks/snippet.html'))), max_num=2))), null=True, verbose_name='Page content'),
        ),
    ]
