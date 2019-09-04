from __future__ import absolute_import, unicode_literals

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import redirect, render

from wagtail.core.models import Page
from wagtail.search.models import Query

from categories.models import RowComponent
from exhibitions.models import ExhibitPage


def search(request):
    """
    Handle HTTP search requests. Depending on the searchType GET parameter, a few
    things could happen:
        "all" -> redirect to Summon search
        "services" -> query all Wagtail pages & render
        "exhibits" -> query just Exhibit pages & render
        "catalog" -> redirect to Koha search
    Of these four options, neither catalog nor exhibits are actually exposed to
    end users; they're just there in case we need them internally or want to add
    this functionality later.
    """
    search_query = request.GET.get('q', None)
    page = request.GET.get('page', 1)

    # redirect Summon & Koha searches accordingly, default to Summon
    type = request.GET.get('searchType', 'all')
    if type == 'all':
        summon_url = 'https://cca.summon.serialssolutions.com/'
        # going to /search (no query) -> Summon home page
        if search_query:
            return redirect(summon_url + '?q=' + search_query, permanent=True)
        else:
            return redirect(summon_url)
    elif type == 'catalog':
        koha_url = 'https://library.cca.edu/cgi-bin/koha/opac-search.pl?&q='
        return redirect(koha_url + search_query, permanent=True)

    # Search
    if type == 'services' and search_query:
        # exclude RowComponent pages
        search_results = Page.objects.not_type(RowComponent).live().search(search_query)
        query = Query.get(search_query)
        # Record hit
        query.add_hit()
    elif type == 'exhibits' and search_query:
        search_results = Page.objects.type(ExhibitPage).live().search(search_query)
        query = Query.get(search_query)
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
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
