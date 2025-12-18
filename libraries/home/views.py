from categories.models.pages import RowComponent
from wagtail.admin.views.reports import PageReportView, ReportView
from wagtail.images import get_image_model
from wagtail.models import Page


# https://docs.wagtail.io/en/stable/advanced_topics/adding_reports.html
class NoSearchDescriptionReport(PageReportView):
    def get_queryset(self):
        # Pages without a search_description sorted reverse chronologically by last updated
        return (
            Page.objects.not_type(RowComponent)
            .filter(search_description="", depth__gte=2)
            .order_by("-last_published_at")
        )

    header_icon = "search"
    page_title = "Pages lacking a Search Description"
    template_name = "wagtailadmin/reports/base_page_report.html"


class UnusedImagesReport(ReportView):
    """Report showing images that are not used anywhere in the site."""

    header_icon = "image"
    page_title = "Unused Images"
    template_name = "reports/unused_images_report.html"

    def get_queryset(self):
        Image = get_image_model()
        # Get all unused images
        images = Image.objects.all()
        unused_image_pks = set()

        # omit images in the Instagram collection—we store alt text elsewhere
        ig_images = Image.objects.filter(collection__name="Instagram")
        images = images.difference(ig_images)

        for img in images:
            if not len(img.get_usage()):
                unused_image_pks.add(img.pk)

        # Return queryset of unused images sorted by most recently created
        return Image.objects.filter(pk__in=unused_image_pks).order_by("-created_at")

    def get_filename(self):
        return "unused-images-report"
