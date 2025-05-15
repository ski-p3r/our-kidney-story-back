from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from stories.models import Tag

class ProductCategory(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Product Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, related_name='products', blank=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title

class ProductReview(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')
    
    def __str__(self):
        return f"Review by {self.user.get_full_name()} for {self.product.title}"

class Cart(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    
    def __str__(self):
        return f"Cart for {self.user.get_full_name()}"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
    
    @property
    def subtotal(self):
        return self.product.price * self.quantity

class Wishlist(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='wishlists')
    
    def __str__(self):
        return f"Wishlist for {self.user.get_full_name()}"

class Order(TimeStampedModel):
    ORDER_STATUS = (
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default='PENDING')
    shipping_address = models.TextField()
    contact_number = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.id} by {self.user.get_full_name()}"

class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of purchase
    
    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
    
    @property
    def subtotal(self):
        return self.price * self.quantity
