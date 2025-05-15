from django.contrib import admin
from .models import (
    ProductCategory, Product, ProductReview,
    Cart, CartItem, Wishlist,
    Order, OrderItem
)

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'in_stock', 'created_at')
    list_filter = ('category', 'in_stock')
    search_fields = ('title', 'description', 'category__name', 'tags__name')
    autocomplete_fields = ('category', 'tags')
    ordering = ('title',)

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('product__title', 'user__first_name', 'user__last_name', 'comment')
    autocomplete_fields = ('product', 'user')
    ordering = ('-created_at',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'total')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('total',)
    ordering = ('-updated_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'subtotal', 'created_at')
    search_fields = ('cart__user__first_name', 'cart__user__last_name', 'product__title')
    autocomplete_fields = ('cart', 'product')
    readonly_fields = ('subtotal',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    filter_horizontal = ('products',)
    ordering = ('-updated_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__first_name', 'user__last_name', 'contact_number', 'shipping_address')
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'subtotal')
    search_fields = ('order__id', 'product__title')
    autocomplete_fields = ('order', 'product')
    readonly_fields = ('subtotal',)
