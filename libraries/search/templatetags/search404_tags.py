from django import template
from django.urls import reverse

from wagtail.core.models import Page
from urllib.parse import unquote_plus

from categories.models import RowComponent

# most code swiped shamelessly from https://github.com/alexgleason/wagtailerrorpages
register = template.Library()


@register.inclusion_tag('search/search_404.html', takes_context=True)
def search_404(context, max_results=5):
    url_path = context['request'].path_info
    search_query = unquote_plus(url_path).replace('/', ' ')
    search_results = Page.objects.not_type(RowComponent).live().public().search(search_query)[0:max_results]
    search = True

    try:
        # Some sites may not have search.
        reverse('search')
    except:
        search = False

    return {
        'search': search,
        'search_query': search_query,
        'search_results': search_results,
    }
