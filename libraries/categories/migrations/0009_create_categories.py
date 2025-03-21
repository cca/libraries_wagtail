# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-18 00:36
from __future__ import unicode_literals

from django.db import migrations
from wagtail.models import Page


# create the initial About Us, Collections, and Services pages
def create_categories(apps, schema_editor):
    # Get models
    ContentType = apps.get_model('contenttypes.ContentType')
    CategoryPage = apps.get_model('categories.CategoryPage')

    # Delete any existing pages with same slug (no matter their model)
    # if migration is run multiple times
    Page.objects.filter(slug='about-us', depth=3).delete()
    Page.objects.filter(slug='collections', depth=3).delete()
    Page.objects.filter(slug='services', depth=3).delete()

    # Get content type for category page
    categorypage_content_type, __ = ContentType.objects.get_or_create(
        model='categorypage', app_label='categories')

    home_page = Page.objects.get(slug='home')

    about_us = CategoryPage(
        title="About Us",
        slug='about-us',
        content_type=categorypage_content_type,
        depth=3,
        url_path='/home/about-us/'
    )
    collections = CategoryPage(
        title="Collections",
        slug='collections',
        content_type=categorypage_content_type,
        depth=3,
        url_path='/home/collections/'
    )
    services = CategoryPage(
        title="Services",
        slug='services',
        content_type=categorypage_content_type,
        depth=3,
        url_path='/home/services/'
    )

    # Create a new blogindex as child of home page
    home_page.add_child(instance=about_us)
    home_page.add_child(instance=collections)
    home_page.add_child(instance=services)


def remove_categories(apps, schema_editor):
    # Get models
    CategoryPage = apps.get_model('categories.CategoryPage')

    # Delete the default blogindex
    # Page and Site objects CASCADE
    CategoryPage.objects.filter(slug='about-us', depth=3).delete()
    CategoryPage.objects.filter(slug='collections', depth=3).delete()
    CategoryPage.objects.filter(slug='services', depth=3).delete()


class Migration(migrations.Migration):
    run_before = [
        # added for Wagtail 2.11 compatibility
        ('wagtailcore', '0053_locale_model'),
    ]

    # we need the CategoryPage model to already exist
    dependencies = [
        ('categories', '0008_auto_20170721_0453'),
        ('home', '0002_create_homepage'),
    ]

    operations = [
        migrations.RunPython(create_categories, remove_categories),
    ]
