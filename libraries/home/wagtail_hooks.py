from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .views import NoSearchDescriptionReport, UnusedImagesReport


# add our wiki to the "help" section of the main admin menu
# doesn't belong under home but hooks don't work in main "libraries" directory
@hooks.register("register_help_menu_item")  # type: ignore
def register_libraries_wiki_menu_item():
    return MenuItem(
        "Libraries Wiki",
        "https://sites.google.com/cca.edu/librarieswiki/home/websites-servers/editing-in-wagtail",
        classname="icon icon-help",
        order=0,
    )


@hooks.register("register_reports_menu_item")  # type: ignore
def register_no_search_desc_report_menu_item():
    return MenuItem(
        "Pages lacking Search Description",
        reverse("no_search_description_report"),
        icon_name=NoSearchDescriptionReport.header_icon,
        order=700,
    )


@hooks.register("register_reports_menu_item")  # type: ignore
def register_unused_images_report_menu_item():
    return MenuItem(
        "Unused Images",
        reverse("unused_images_report"),
        icon_name=UnusedImagesReport.header_icon,
        order=710,
    )


@hooks.register("register_admin_urls")  # type: ignore
def register_no_search_desc_report_url():
    return [
        path(
            "reports/no-search-description/",
            NoSearchDescriptionReport.as_view(),
            name="no_search_description_report",
        ),
    ]


@hooks.register("register_admin_urls")  # type: ignore
def register_unused_images_report_url():
    return [
        path(
            "reports/unused-images/",
            UnusedImagesReport.as_view(),
            name="unused_images_report",
        ),
    ]
