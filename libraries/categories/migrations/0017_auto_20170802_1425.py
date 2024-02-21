# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-02 21:25
from __future__ import unicode_literals

import categories.models
from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0016_externallink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicepage',
            name='body',
            field=wagtail.fields.StreamField((('subheading', wagtail.blocks.CharBlock(classname='title', icon='title', template='categories/blocks/subheading.html')), ('paragraph', wagtail.blocks.RichTextBlock(icon='pilcrow', template='categories/blocks/paragraph.html')), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(blank=True))))), ('pullquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('name', wagtail.blocks.CharBlock(blank=True)), ('position', wagtail.blocks.CharBlock(blank=True, label='Position or affiliation'))))), ('snippet', wagtail.blocks.RichTextBlock(label='Callout', template='categories/blocks/snippet.html')), ('html', categories.models.EmbedHTML(label='Embed code')), ('row', wagtail.blocks.StreamBlock((('paragraph', wagtail.blocks.RichTextBlock(icon='pilcrow', template='categories/blocks/paragraph.html')), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(blank=True))))), ('pullquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('name', wagtail.blocks.CharBlock(blank=True)), ('position', wagtail.blocks.CharBlock(blank=True, label='Position or affiliation'))))), ('snippet', wagtail.blocks.RichTextBlock(label='Callout', template='categories/blocks/snippet.html')))))), null=True, verbose_name='Page content'),
        ),
    ]
