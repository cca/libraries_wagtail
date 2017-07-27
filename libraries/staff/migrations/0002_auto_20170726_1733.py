# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-26 17:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffmember',
            name='email',
            field=models.EmailField(default='username@cca.edu', max_length=254),
        ),
        migrations.AlterField(
            model_name='staffmember',
            name='phone',
            field=models.CharField(blank=True, default='415.703.5555', help_text='In form "555.555.5555"', max_length=12),
        ),
    ]
