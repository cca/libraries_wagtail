import logging

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import redirect, render

from wagtail.models import Page
from wagtail.search.models import Query

from exhibitions.models import ExhibitPage

logger = logging.getLogger(__name__)


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
    search_query = request.GET.get("q", None)
    page = request.GET.get("page", 1)

    # redirect Summon & Koha searches accordingly, default to Summon
    type = request.GET.get("searchType", "all")
    if type == "all":
        summon_url = "https://cca.summon.serialssolutions.com/"
        # going to /search (no query) -> Summon home page
        if search_query:
            logger.info("Summon search, query: {}".format(search_query))
            # disable Book Review content type by default issue #87
            return redirect(
                summon_url + "?fvf=ContentType,Book%20Review,t&q=" + search_query,
                permanent=True,
            )
        else:
            return redirect(summon_url)
    elif type == "catalog":
        # ! we don't expose this koha search anywhere
        logger.info("Koha search, query: {}".format(search_query))
        koha_url = "https://library.cca.edu/cgi-bin/koha/opac-search.pl?&q="
        return redirect(koha_url + search_query, permanent=True)

    # Search
    if type == "services" and search_query:
        logger.info("Wagtail search, query: {}".format(search_query))
        # decided against Fuzzy matching, returns too many irrelevant results
        # every search returns almost every page on the site
        # https://docs.wagtail.org/en/stable/topics/search/searching.html#fuzzy-matching
        # Wagtail 5.0 disabled partial matches in ES so we switched to use .autocomplete
        # https://docs.wagtail.org/en/stable/releases/5.0.html#elasticsearch-backend-no-longer-performs-partial-matching-on-search
        search_results = Page.objects.live().autocomplete(search_query, operator="and")
        # ? What is Query doing here?
        # ! Also it should come from wagtail.contrib.search_promotions & not wagtailsearch.Query
        query = Query.get(search_query)
        # Record hit
        query.add_hit()
    elif type == "exhibits" and search_query:
        # ! we don't expose exhibits search anywhere
        logger.info("Exhibits search, query: {}".format(search_query))
        search_results = (
            Page.objects.type(ExhibitPage)
            .live()
            .autocomplete(search_query, operator="and")
        )
        # ? What is Query doing here?
        # ! Also it should come from wagtail.contrib.search_promotions & not wagtailsearch.Query
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

    return render(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
        },
    )
