from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import ForumCategory, ForumThread, ForumPost, ReportedContent
from .serializers import (
    ForumCategorySerializer,
    ForumThreadSerializer,
    ForumThreadCreateUpdateSerializer,
    ForumThreadDetailSerializer,
    ForumPostSerializer,
    ForumPostCreateSerializer,
    ReportedContentSerializer,
    ReportedContentCreateSerializer
)
from core.permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin, IsAdminUser

class ForumCategoryViewSet(viewsets.ModelViewSet):
    queryset = ForumCategory.objects.all()
    serializer_class = ForumCategorySerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

class ForumThreadViewSet(viewsets.ModelViewSet):
    queryset = ForumThread.objects.all()
    serializer_class = ForumThreadSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'user', 'is_pinned', 'is_closed']
    search_fields = ['title']
    ordering_fields = ['created_at', 'views']
    ordering = ['-is_pinned', '-created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        elif self.action in ['pin', 'close']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ForumThreadDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ForumThreadCreateUpdateSerializer
        return ForumThreadSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        thread = self.get_object()
        thread.is_pinned = not thread.is_pinned
        thread.save()
        return Response({'status': 'pinned' if thread.is_pinned else 'unpinned'})
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        thread = self.get_object()
        thread.is_closed = not thread.is_closed
        thread.save()
        return Response({'status': 'closed' if thread.is_closed else 'opened'})

class ForumPostViewSet(viewsets.ModelViewSet):
    queryset = ForumPost.objects.all()
    serializer_class = ForumPostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['thread', 'user']
    
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
            return ForumPostCreateSerializer
        return ForumPostSerializer
    
    def get_queryset(self):
        queryset = ForumPost.objects.all()
        
        # Filter by thread if provided
        thread_id = self.request.query_params.get('thread', None)
        if thread_id:
            queryset = queryset.filter(thread_id=thread_id)
            
        # Only get top-level posts if specified
        top_level = self.request.query_params.get('top_level', None)
        if top_level and top_level.lower() == 'true':
            queryset = queryset.filter(parent=None)
            
        return queryset
    
    def perform_create(self, serializer):
        thread = ForumThread.objects.get(id=serializer.validated_data['thread'].id)
        
        # Check if thread is closed
        if thread.is_closed:
            raise serializers.ValidationError("This thread is closed and cannot receive new posts.")
            
        serializer.save(user=self.request.user)

class ReportedContentViewSet(viewsets.ModelViewSet):
    queryset = ReportedContent.objects.all()
    serializer_class = ReportedContentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['content_type', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportedContentCreateSerializer
        return ReportedContentSerializer
    
    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
