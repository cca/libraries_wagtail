from alerts.models import Alert
from rest_framework import serializers


class AlertSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Alert
        fields = [
            "id",
            "url",
            "last_published_at",
            "alert_text",
            "alert_link",
            "alert_link_text",
        ]
