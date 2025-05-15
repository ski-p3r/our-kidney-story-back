from rest_framework import viewsets, status, filters
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
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
from .serializers import (
    ProductCategorySerializer,
    ProductSerializer,
    ProductCreateUpdateSerializer,
    ProductDetailSerializer,
    ProductReviewSerializer,
    CartSerializer,
    CartItemSerializer,
    CartItemCreateUpdateSerializer,
    WishlistSerializer,
    WishlistItemCreateSerializer,   
    OrderSerializer,
    OrderCreateSerializer
)
from core.permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin, IsAdminUser

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'in_stock', 'tags__name']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'])
    def filter_by_price(self, request):
        min_price = request.query_params.get('min', None)
        max_price = request.query_params.get('max', None)
        
        queryset = self.get_queryset()
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'user', 'rating']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Check if user already reviewed this product
        product = serializer.validated_data['product']
        user = self.request.user
        
        # Check if user bought this product
        if not OrderItem.objects.filter(order__user=user, product=product).exists():
            raise ValidationError({"detail": "You can only review products you have purchased."})
        
        if ProductReview.objects.filter(product=product, user=user).exists():
            raise ValidationError({"detail": "You have already reviewed this product."})
        
        
        serializer.save(user=user)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]  # Only owner can view their cart
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        # Ensure each user has a cart
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CartItemCreateUpdateSerializer
        return CartItemSerializer

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        # Check if product is in stock
        if not product.in_stock:
            raise ValidationError({'error': 'Product is out of stock'})

        existing_item = CartItem.objects.filter(cart=cart, product=product).first()
        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
        else:
            serializer.save(cart=cart)
            
            
class WishlistViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)

    def create(self, request):
        serializer = WishlistItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product']
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

        if wishlist.products.filter(id=product.id).exists():
            return Response({"detail": "Product already in wishlist."}, status=status.HTTP_400_BAD_REQUEST)

        wishlist.products.add(product)
        return Response({"detail": "Product added to wishlist."}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='remove')
    def remove(self, request):
        product_id = request.data.get('product')
        if not product_id:
            return Response({'error': 'Product ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product = Product.objects.filter(id=product_id).first()

        if not product or not wishlist.products.filter(id=product.id).exists():
            return Response({'error': 'Product not in wishlist.'}, status=status.HTTP_400_BAD_REQUEST)

        wishlist.products.remove(product)
        return Response({"detail": "Product removed from wishlist."}, status=status.HTTP_200_OK)
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if cart has items
        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create order
        order = Order.objects.create(
            user=user,
            shipping_address=serializer.validated_data['shipping_address'],
            contact_number=serializer.validated_data['contact_number'],
            total_amount=cart.total
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        # Clear cart
        cart.items.all().delete()
        
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Only admins can update order status'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        order = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if status_value not in dict(Order.ORDER_STATUS):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        order.status = status_value
        order.save()
        
        return Response(OrderSerializer(order).data)
