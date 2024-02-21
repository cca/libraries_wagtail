# Generated by Django 2.2.7 on 2019-11-12 00:45

import categories.models.blocks
from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0033_sidebar_resources'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicepage',
            name='body',
            field=wagtail.fields.StreamField([('subheading', wagtail.blocks.CharBlock(classname='title', icon='title', template='categories/blocks/subheading.html')), ('paragraph', wagtail.blocks.RichTextBlock(features=['bold', 'document-link', 'italic', 'link', 'strikethrough', 'subscript', 'superscript', 'code', 'embed', 'h3', 'hr', 'image', 'ol', 'ul'], icon='pilcrow', template='categories/blocks/paragraph.html')), ('linked_image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'document-link', 'italic', 'link', 'strikethrough', 'subscript', 'superscript'], required=False)), ('external_url', wagtail.blocks.URLBlock(help_text="Only one of these (external URL or internal page) is needed. You can leave both blank if you don't want the image to be linked.", label='External URL', required=False)), ('page', wagtail.blocks.PageChooserBlock(label='Internal web page', required=False))])), ('card', wagtail.blocks.StructBlock([('thumbnail', wagtail.images.blocks.ImageChooserBlock(help_text='Should be 3x2 aspect ratio but may be stretched if used in a row without an equal distribution. Resized to roughly 345x230.')), ('link', wagtail.blocks.StructBlock([('text', wagtail.blocks.CharBlock(label='Link text', required=True)), ('external_url', wagtail.blocks.URLBlock(label='External URL', required=False)), ('page', wagtail.blocks.PageChooserBlock(label='Internal web page', required=False))])), ('body', wagtail.blocks.RichTextBlock(features=['bold', 'document-link', 'italic', 'link', 'strikethrough', 'subscript', 'superscript']))])), ('pullquote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.TextBlock('quote title')), ('name', wagtail.blocks.CharBlock(required=False)), ('position', wagtail.blocks.CharBlock(label='Position or affiliation', required=False))])), ('snippet', wagtail.blocks.RichTextBlock(label='Callout', template='categories/blocks/snippet.html')), ('html', categories.models.blocks.EmbedHTML(label='Embed code')), ('row', wagtail.blocks.StreamBlock([('distribution', wagtail.blocks.ChoiceBlock(blank=False, choices=[('left', 'left side bigger'), ('right', 'right side bigger'), ('equal', 'equal size sides')], max_num=1, min_num=1)), ('paragraph', wagtail.blocks.RichTextBlock(features=['bold', 'document-link', 'italic', 'link', 'strikethrough', 'subscript', 'superscript', 'code', 'embed', 'h3', 'hr', 'image', 'ol', 'ul'], icon='pilcrow', template='categories/blocks/paragraph.html')), ('linked_image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'document-link', 'italic', 'link', 'strikethrough', 'subscript', 'superscript'], required=False)), ('external_url', wagtail.blocks.URLBlock(help_text="Only one of these (external URL or internal page) is needed. You can leave both blank if you don't want the image to be linked.", label='External URL', required=False)), ('page', wagtail.blocks.PageChooserBlock(label='Internal web page', required=False))])), ('card', wagtail.blocks.StructBlock([('thumbnail', wagtail.images.blocks.ImageChooserBlock(help_text='Should be 3x2 aspect ratio but may be stretched if used in a row without an equal distribution. Resized to roughly 345x230.')), ('link', wagtail.blocks.StructBlock([('text', wagtail.blocks.CharBlock(label='Link text', required=True)), ('external_url', wagtail.blocks.URLBlock(label='External URL', required=False)), ('page', wagtail.blocks.PageChooserBlock(label='Internal web page', required=False))])), ('body', wagtail.blocks.RichTextBlock(features=['bold', 'document-link', 'italic', 'link', 'strikethrough', 'subscript', 'superscript']))])), ('pullquote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.TextBlock('quote title')), ('name', wagtail.blocks.CharBlock(required=False)), ('position', wagtail.blocks.CharBlock(label='Position or affiliation', required=False))])), ('snippet', wagtail.blocks.RichTextBlock(features=['bold', 'document-link', 'italic', 'link', 'strikethrough', 'subscript', 'superscript', 'code', 'embed', 'h3', 'hr', 'image', 'ol', 'ul'], label='Callout', template='categories/blocks/snippet.html'))], max_num=3))], null=True, verbose_name='Page content'),
        ),
    ]
