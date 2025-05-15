from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryViewSet,
    ProductViewSet,
    ProductReviewViewSet,
    CartViewSet,
    CartItemViewSet,
    WishlistViewSet,
    OrderViewSet
)

router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet)
router.register(r'reviews', ProductReviewViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
