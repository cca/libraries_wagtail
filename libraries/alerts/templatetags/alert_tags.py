from models import AlertPage, NotificationPage
register = template.Library()

@register.simple_tag
def show_alert_banner():
    return bool(AlertPage.objects.filter(live=True))

@register.simple_tag
def alert_banner():
    return AlertPage.objects.filter(live=True).order_by("-last_published_at").first()

@register.simple_tag
def show_notification_banner():
    return bool(NotificationPage.objects.filter(live=True) and not AlertPage.objects.filter(live=True))

@register.simple_tag
def notification_banner():
    return NotificationPage.objects.filter(live=True).order_by("-last_published_at").first()
