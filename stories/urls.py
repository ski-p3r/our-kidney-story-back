from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoryViewSet, CommentViewSet, TagViewSet

router = DefaultRouter()
router.register(r'comments', CommentViewSet)
router.register(r'tags', TagViewSet)
router.register(r'', StoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
