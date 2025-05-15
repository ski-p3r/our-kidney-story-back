from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogViewSet, BlogCommentViewSet

router = DefaultRouter()
router.register(r'comments', BlogCommentViewSet)
router.register(r'', BlogViewSet, basename='blog')

urlpatterns = [
    path('', include(router.urls)),
]
