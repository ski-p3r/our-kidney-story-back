from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ForumCategoryViewSet, ForumThreadViewSet, ForumPostViewSet, ReportedContentViewSet

router = DefaultRouter()
router.register(r'categories', ForumCategoryViewSet)
router.register(r'threads', ForumThreadViewSet)
router.register(r'posts', ForumPostViewSet)
router.register(r'reports', ReportedContentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
