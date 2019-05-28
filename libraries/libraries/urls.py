from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

from brokenlinks import views as brokenlinks_views
from hours import views as hours_views
from libraries.views import serve_wagtail_doc
from search import views as search_views
from sersol_api import views as sersol_views

from .api import api_router

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls


urlpatterns = [
    url(r'^django-admin/', admin.site.urls),
    # override Wagtail document handling — send file, not a forced download
    url(r'^documents/(\d+)/(.*)$', serve_wagtail_doc, name='wagtaildocs_serve'),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^api/v2/', api_router.urls),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^search/$', search_views.search, name='search'),
    url(r'^hours/$', hours_views.hours, name='hours'),

    # Summon "broken links" app
    url(r'^brokenlinks/$', brokenlinks_views.brokenlinks, name='brokenlinks'),

    # Serials Solution API proxy
    url(r'^sersol/$', sersol_views.sersol, name='sersol_api'),

    # Favicon
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True)),
    # Robots.txt
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    # XML sitemap
    url('^sitemap\.xml$', sitemap),

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    url(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
