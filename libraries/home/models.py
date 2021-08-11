from django.conf import settings
from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel

from blog.models import all_blog_posts
from exhibitions.models import ExhibitPage
from hours.models import get_open_hours
from instagram.models import Instagram


class HomePage(Page):
    background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        on_delete=models.PROTECT,
        related_name='+',
        help_text='ideal dimensions are 1440x630px, please optimize image size too!',
    )

    # for search result template
    def _get_image(self):
        return self.background_image

    main_image = property(_get_image)

    image_attribution = RichTextField(features=settings.RICHTEXT_BASIC, blank=True)

    # @TODO this is a quick, emergency hack to get links into the description
    # we should redo these as StructBlocks with a title, link, & rich text
    services_text = RichTextField(features=settings.RICHTEXT_BASIC, blank=True)
    collections_text = RichTextField(features=settings.RICHTEXT_BASIC, blank=True)
    about_us_text = RichTextField(features=settings.RICHTEXT_BASIC, blank=True)

    # commented out are the actual, allowed subpages but they are singletons &
    # auto generated by migrations so we disable adding them here
    subpage_types = [
        # 'blog.BlogIndex',
        # 'categories.CategoryPage',
        'exhibitions.ExhibitsIndexPage',
    ]

    # don't allow more home pages to be created
    parent_page_types = []

    content_panels = Page.content_panels + [
        ImageChooserPanel('background_image'),
        FieldPanel('image_attribution'),
        MultiFieldPanel([
            FieldPanel('services_text'),
            FieldPanel('collections_text'),
            FieldPanel('about_us_text'),
        ], heading="Category Descriptions")
    ]

    def get_context(self, request):
        context = super(HomePage, self).get_context(request)

        # add latest 2 blog posts as "news items"
        news_items = all_blog_posts()[:2]
        # if we have a featured exhibit, it replaces the second blog post
        featured_exhibit = ExhibitPage.objects.filter(featured=True).last()
        if featured_exhibit:
            news_items[1] = featured_exhibit
        context['news_items'] = news_items
        # pull open hours snippets for today
        context['hours'] = get_open_hours()

        # add instagram
        context['instagram'] = Instagram.objects.last()

        return context
