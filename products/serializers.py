from rest_framework import serializers
from .models import (
    ProductCategory, 
    Product, 
    ProductReview, 
    Cart, 
    CartItem, 
    Wishlist, 
    Order, 
    OrderItem
)
from users.serializers import UserSerializer
from stories.serializers import TagSerializer

class ProductCategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'product_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_product_count(self, obj):
        return obj.products.count()

class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'image_url', 'category', 'price', 
                  'in_stock', 'tags', 'average_rating', 'review_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.count()

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False
    )
    
    class Meta:
        model = Product
        fields = ['title', 'description', 'image_url', 'category', 'price', 'in_stock', 'tags']
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        product = Product.objects.create(**validated_data)
        
        # Process tags
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
            product.tags.add(tag)
        
        return product
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
                instance.tags.add(tag)
        
        return instance

class ProductDetailSerializer(ProductSerializer):
    reviews = ProductReviewSerializer(many=True, read_only=True)
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['reviews']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'subtotal']
        read_only_fields = ['id', 'subtotal']

class CartItemCreateUpdateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total']
        read_only_fields = ['id', 'total']


class WishlistItemCreateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Wishlist
        fields = ['product']
        
class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'products']
        read_only_fields = ['id']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'subtotal']
        read_only_fields = ['id', 'price', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'shipping_address', 'contact_number', 
                  'total_amount', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['shipping_address', 'contact_number']
