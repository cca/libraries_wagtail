# Generated by Django 2.1.7 on 2019-04-09 23:51

import categories.models
from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('exhibitions', '0006_exhib_display'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exhibitartwork',
            name='embed_code',
            field=models.TextField(blank=True, help_text='Also used for YouTube or Vimeo. Just copy the URL of the video e.g. https://www.youtube.com/watch?v=F1B9Fk_SgI0 and not the full <iframe> wrapped HTML.'),
        ),
        migrations.AlterField(
            model_name='exhibitpage',
            name='description',
            field=wagtail.fields.StreamField([('subheading', wagtail.blocks.CharBlock(classname='title', icon='title', template='categories/blocks/subheading.html')), ('paragraph', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link', 'h3', 'ol', 'ul', 'image', 'embed', 'hr'], icon='pilcrow', template='categories/blocks/paragraph.html')), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link'], required=False))])), ('linked_image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link'], required=False)), ('link', wagtail.blocks.URLBlock())])), ('pullquote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.TextBlock('quote title')), ('name', wagtail.blocks.CharBlock(required=False)), ('position', wagtail.blocks.CharBlock(label='Position or affiliation', required=False))])), ('snippet', wagtail.blocks.RichTextBlock(label='Callout', template='categories/blocks/snippet.html')), ('html', categories.models.EmbedHTML(label='Embed code')), ('row', wagtail.blocks.StreamBlock([('distribution', wagtail.blocks.ChoiceBlock(blank=False, choices=[('left', 'left side bigger'), ('right', 'right side bigger'), ('equal', 'equal size sides')], max_num=1, min_num=1)), ('paragraph', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link', 'h3', 'ol', 'ul', 'image', 'embed', 'hr'], icon='pilcrow', template='categories/blocks/paragraph.html')), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link'], required=False))])), ('linked_image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link'], required=False)), ('link', wagtail.blocks.URLBlock())])), ('pullquote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.TextBlock('quote title')), ('name', wagtail.blocks.CharBlock(required=False)), ('position', wagtail.blocks.CharBlock(label='Position or affiliation', required=False))])), ('snippet', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'document-link', 'h3', 'ol', 'ul', 'image', 'embed', 'hr'], label='Callout', template='categories/blocks/snippet.html'))], max_num=3))], null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='headerimage',
            name='image',
            field=models.ForeignKey(help_text='Single header images should be ≥ 1360px wide; they will be strecthed if not. Foursquare images are sized to a 400x400 square but you can upload larger images.', on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailimages.Image'),
        ),
    ]
