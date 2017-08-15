from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem

# add a "help" section to admin menu that links out to our Google wiki
# doesn't belong under home but hooks don't work in main "libraries" directory
@hooks.register('register_admin_menu_item')
def register_frank_menu_item():
    return MenuItem(
        'Help',
        'https://sites.google.com/a/cca.edu/libraries/home/websites-servers/editing-in-wagtail',
        classnames='icon icon-help',
        order=10000,
    )
