from wagtail.admin.views.reports import PageReportView
from wagtail.models import Page

from categories.models.pages import RowComponent


# https://docs.wagtail.io/en/stable/advanced_topics/adding_reports.html
class NoSearchDescriptionReport(PageReportView):

    def get_queryset(self):
        # Pages without a search_description sorted reverse chronologically by last updated
        return (
            Page.objects.not_type(RowComponent)
            .filter(search_description="", depth__gte=2)
            .order_by("-last_published_at")
        )

    title = "Pages lacking a Search Description"
    header_icon = "search"
