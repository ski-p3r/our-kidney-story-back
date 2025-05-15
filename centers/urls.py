from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DialysisCenterViewSet

router = DefaultRouter()
router.register(r'', DialysisCenterViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
