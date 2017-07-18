from django.db import models
from django.shortcuts import render

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index


def latest_posts():
    return BlogPage.objects.live().order_by('-first_published_at')


# we don't really use a blog index page but we need this here
# for the home > blog index > blog page URL hierarcy
# @TODO if someone visits the blog index's slug "/blog/"
# they should be redirected to the latest blog post
class BlogIndex(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['blog.BlogPage']

    # override serve to redirect to latest blog post if index is visited
    def serve(self, request):
        post = BlogPage.objects.live().latest('first_published_at')
        return render(request, BlogPage.template, {
            'other_posts': latest_posts(),
            'page': post,
        })


class BlogPage(Page):
    parent_page_types = ['blog.BlogIndex']
    subpage_types = []

    date = models.DateField("Post date")
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Try to ALWAYS provide a main image.'
    )
    # for backwards compatibility with our Drupal blog posts
    imported_body = RichTextField(
        blank=True,
        help_text='Do NOT use this field! It is only for imported data from our old site.'
    )
    # @TODO a streamfield for the body block of new (not imported) posts

    # add latest blog posts to context
    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(BlogPage, self).get_context(request)
        other_posts = latest_posts()
        context['other_posts'] = other_posts
        return context

    search_fields = Page.search_fields + [
        index.SearchField('imported_body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        ImageChooserPanel('main_image'),
        FieldPanel('imported_body'),
    ]
    pass
