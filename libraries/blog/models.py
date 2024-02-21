from django.db import models
from django.shortcuts import render

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index

from categories.models import BaseStreamBlock
from libraries.utils import validate_clean


# helper to get a list of published blog posts in reverse chronological order
def all_blog_posts():
    blogs = list(BlogPage.objects.live().order_by("-date"))
    # pad the blogs list with 2 None values so there's no error if we
    # have no posts (e.g. when a new site instance is created)
    while len(blogs) < 2:
        blogs.append(None)

    return blogs


# we don't really use a blog index page but we need this here
# for the home > blog index > blog page URL hierarcy
class BlogIndex(Page):
    parent_page_types = ["home.HomePage"]
    subpage_types = ["blog.BlogPage"]
    max_count = 1

    # override serve to redirect to latest blog post if index is visited
    def serve(self, request):
        latest_posts = all_blog_posts()[:5]

        return render(
            request,
            BlogPage.template,
            {
                "latest_posts": latest_posts,
                "next_post": None,
                "page": latest_posts[0],
                "previous_post": latest_posts[1],
            },
        )

    # allow only one instance of this page type
    @classmethod
    def can_create_at(cls, parent):
        return super(BlogIndex, cls).can_create_at(parent) and not cls.objects.exists()

    class Meta:
        verbose_name = "News index"


class BlogPage(Page):
    parent_page_types = ["blog.BlogIndex"]
    subpage_types = []

    date = models.DateField("Post date")
    main_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
        help_text="Resized to 400x267px for the home page thumbnail and 700px wide on the post itself with a preserved aspect ratio.",
    )

    # we reuse the same StreamField from categories
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page content", null=True, use_json_field=True
    )

    # for backwards compatibility with our Drupal blog posts
    # this should be the _only_ rich text field without a "features" property
    # since we have no idea what the incoming HTML could be
    imported_body = RichTextField(
        blank=True,
        help_text="Do NOT use this field! It is only for imported data from our old site.",
    )

    # add latest, next, & previous blog posts to context
    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(BlogPage, self).get_context(request)

        all_posts = all_blog_posts()

        # all_posts is all _published_ posts so a draft preview won't be in it
        try:
            index = all_posts.index(self)
        except:
            index = 0

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

        context["latest_posts"] = all_posts[:5]
        context["next_post"] = next_post
        context["previous_post"] = previous_post

        return context

    def clean(self):
        super().clean()
        validate_clean(self)

    class Meta:
        verbose_name = "News article"

    search_fields = Page.search_fields + [
        index.SearchField("imported_body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("main_image"),
        FieldPanel("body"),
        FieldPanel("imported_body"),
    ]
