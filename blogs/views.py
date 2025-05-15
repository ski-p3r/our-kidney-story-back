from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Blog, BlogComment
from .serializers import (
    BlogSerializer, 
    BlogCreateUpdateSerializer, 
    BlogCommentSerializer, 
    BlogCommentCreateSerializer
)
from core.permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin, IsAdminUser

class BlogViewSet(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tags__name', 'author__id', 'published']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'views']
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == 'ADMIN':
            return Blog.objects.all()
        elif self.request.user.is_authenticated:
            # Show published blogs and user's own unpublished blogs
            return Blog.objects.filter(
                models.Q(published=True) | 
                models.Q(published=False, author=self.request.user)
            )
        else:
            # Show only published blogs to anonymous users
            return Blog.objects.filter(published=True)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BlogCreateUpdateSerializer
        return BlogSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class BlogCommentViewSet(viewsets.ModelViewSet):
    queryset = BlogComment.objects.filter(parent=None)  # Only top-level comments
    serializer_class = BlogCommentSerializer
    
    def get_permissions(self):  
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BlogCommentCreateSerializer
        return BlogCommentSerializer
    
    def get_queryset(self):
        queryset = BlogComment.objects.filter(parent=None)  # Only top-level comments
        
        # Filter by blog if provided
        blog_id = self.request.query_params.get('blog', None)
        if blog_id:
            queryset = queryset.filter(blog_id=blog_id)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
