from django.core.cache import cache
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from wagtail.models import Site

from alerts.models import Alert
from .serializers import AlertSerializer

PAGE_ANCESTORS_CACHE_KEY = 'page_ancestors_{page_pk}'


def purge_ancestors_cache(instance, **kwargs):
    cache.delete(PAGE_ANCESTORS_CACHE_KEY.format(page_pk=instance.pk))


class AlertViewset(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['post', 'delete'])
    def clear_site_cache(self, request, pk=None):
        for site in Site.objects.all():
            # clear site cache
            purge_ancestors_cache(site.root_page)

    def create(self, request):
        Alert.objects.all().delete()  # clear any existing alerts, make sure we always only have one
        return super().create(request)
