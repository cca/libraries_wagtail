from rest_framework import routers

from .viewsets import AlertViewset

router = routers.SimpleRouter()
router.register(r"alerts", AlertViewset)
