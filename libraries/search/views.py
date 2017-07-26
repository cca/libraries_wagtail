from __future__ import absolute_import, unicode_literals

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import redirect, render

from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch.models import Query

from categories.models import RowComponent


def search(request):
    search_query = request.GET.get('q', None)
    page = request.GET.get('page', 1)

    # redirect Summon & Koha searches accordingly, default to Summon
    type = request.GET.get('searchType', 'all')
    if type == 'all':
        summon_url = 'https://cca.summon.serialssolutions.com/?q='
        return redirect(summon_url + search_query, permanent=True)
    elif type == 'catalog':
        koha_url = 'http://library.cca.edu/cgi-bin/koha/opac-search.pl?&q='
        return redirect(koha_url + search_query, permanent=True)

    # Search
    if search_query:
        # exclude RowComponent pages
        search_results = Page.objects.not_type(RowComponent).live().search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    # @TODO pagination number should be a setting, not hard-coded
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
    })
