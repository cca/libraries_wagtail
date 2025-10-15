from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView

from alerts.api.routers import router as alerts_router

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

router = DefaultRouter()
router.registry.extend(alerts_router.registry)

urlpatterns += router.urls
