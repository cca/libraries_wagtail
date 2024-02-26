from django.urls import path, reverse

from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .views import NoSearchDescriptionReport


# add our wiki to the "help" section of the main admin menu
# doesn't belong under home but hooks don't work in main "libraries" directory
@hooks.register("register_help_menu_item")
def register_libraries_wiki_menu_item():
    return MenuItem(
        "Libraries Wiki",
        "https://sites.google.com/cca.edu/librarieswiki/home/websites-servers/editing-in-wagtail",
        classnames="icon icon-help",
        order=0,
    )


@hooks.register("register_reports_menu_item")
def register_no_search_desc_report_menu_item():
    return MenuItem(
        "Pages lacking Search Description",
        reverse("no_search_description_report"),
        classnames="icon icon-" + NoSearchDescriptionReport.header_icon,
        order=700,
    )


@hooks.register("register_admin_urls")
def register_no_search_desc_report_url():
    return [
        path(
            "reports/no-search-description/",
            NoSearchDescriptionReport.as_view(),
            name="no_search_description_report",
        ),
    ]
