# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-26 23:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_staffmember_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffmember',
            name='main_image',
            field=models.ForeignKey(help_text='Will be sized 150-by-150px on the staff list page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
    ]
