from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

from django_cas_ng.views import LoginView, LogoutView

from brokenlinks import views as brokenlinks_views
from hours import views as hours_views
from libraries.views import serve_wagtail_doc
from search import views as search_views
from sersol_api import views as sersol_views

from .api import api_router

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core import urls as wagtail_urls

# @TODO modernize this file, use django.urls.path()
# see https://docs.djangoproject.com/en/2.2/ref/urls/
admin.site.site_header = 'CCA Libraries Administration'
admin.autodiscover()

urlpatterns = [
    path('django-admin/', admin.site.urls),
    # override Wagtail document handling — send file, not a forced download
    path('documents/<int:id>/<filename>', serve_wagtail_doc, name='wagtaildocs_serve'),

    # CAS login urls
    # NOTE: ^admin/logout/$ must appear before ^admin/ or it's impossible to logout
    path('login/', LoginView.as_view(), name='cas_ng_login'),
    path('admin/login/', LoginView.as_view(), name='cas_ng_login'),
    path('admin/logout/', LogoutView.as_view(), name='cas_ng_logout'),

    path('admin/', include(wagtailadmin_urls)),
    path('api/v2/', api_router.urls),

    path('search/', search_views.search, name='search'),
    path('hours/', hours_views.hours, name='hours'),

    # Summon "broken links" app
    path('brokenlinks/', brokenlinks_views.brokenlinks, name='brokenlinks'),

    # Serials Solution API proxy
    path('sersol/', sersol_views.sersol, name='sersol_api'),

    # Favicon
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True)),
    # Robots.txt
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    # XML sitemap
    path('sitemap.xml', sitemap),

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    re_path(r'', include(wagtail_urls)),
]

if settings.DEBUG or settings.BASE_URL == 'http://localhost':
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
