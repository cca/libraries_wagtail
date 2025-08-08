from django import template
from django.urls import reverse

from wagtail.models import Page
from urllib.parse import unquote_plus

from categories.models import RowComponent

# most code swiped shamelessly from https://github.com/alexgleason/wagtailerrorpages
register = template.Library()


@register.inclusion_tag("search/search_404.html", takes_context=True)
def search_404(context, max_results=5):
    url_path = context["request"].path_info
    search_query = unquote_plus(url_path).replace("/", " ").replace("-", " ")
    search_results = (
        Page.objects.live()
        .public()
        .not_type(RowComponent)
        .autocomplete(search_query, operator="and")[0:max_results]
    )

    return {
        "search_results": search_results,
    }
