from alerts.models import Alert
from django import template

register = template.Library()


@register.simple_tag
def show_alert_banner():
    return Alert.objects.exists()


@register.simple_tag
def alert_banner():
    return Alert.objects.order_by("-last_published_at").first()
