from django.db import models
from django.shortcuts import render

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index


# helper to get a list of published blog posts in reverse chronological order
def all_blog_posts():
    blogs = BlogPage.objects.live().order_by('-date')
    return list(blogs)


# we don't really use a blog index page but we need this here
# for the home > blog index > blog page URL hierarcy
class BlogIndex(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['blog.BlogPage']

    # override serve to redirect to latest blog post if index is visited
    def serve(self, request):
        latest_posts = all_blog_posts()[:5]

        return render(request, BlogPage.template, {
            'next_post': None,
            'other_posts': latest_posts,
            'page': latest_posts[0],
            'previous_post': latest_posts[1],
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

    # add latest, next, & previous blog posts to context
    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(BlogPage, self).get_context(request)

        all_posts = all_blog_posts()
        index = all_posts.index(self)
        # handle cases where we're on the newest/oldest post
        if index == 0:
            next_post = None
            previous_post = all_posts[index + 1]
        elif index + 1 == len(all_posts):
            next_post = all_posts[index - 1]
            previous_post = None
        else:
            next_post = all_posts[index - 1]
            previous_post = all_posts[index + 1]

        context['latest_posts'] = all_posts[:5]
        context['next_post'] = next_post
        context['previous_post'] = previous_post

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
