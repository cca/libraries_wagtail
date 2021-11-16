from django.urls import path, reverse

from wagtail.core import hooks
from wagtail.admin.menu import MenuItem

from .views import NoSearchDescriptionReport


# add a "help" section to admin menu that links out to our Google wiki
# doesn't belong under home but hooks don't work in main "libraries" directory
@hooks.register('register_admin_menu_item')
def register_frank_menu_item():
    return MenuItem(
        'Help',
        'https://sites.google.com/cca.edu/librarieswiki/home/websites-servers/editing-in-wagtail',
        classnames='icon icon-help',
        order=10000,
    )


@hooks.register('register_reports_menu_item')
def register_no_search_desc_report_menu_item():
    return MenuItem("Pages lacking Search Description", reverse('no_search_description_report'), classnames='icon icon-' + NoSearchDescriptionReport.header_icon, order=700)


@hooks.register('register_admin_urls')
def register_unpublished_changes_report_url():
    return [
        path('reports/no-search-description/', NoSearchDescriptionReport.as_view(), name='no_search_description_report'),
    ]
