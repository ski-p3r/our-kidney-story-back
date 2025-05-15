from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Story, Comment, Tag
from .serializers import (
    StorySerializer, 
    StoryCreateUpdateSerializer, 
    CommentSerializer, 
    CommentCreateSerializer,
    TagSerializer
)
from core.permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all().prefetch_related('tags')
    serializer_class = StorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tags__name', 'user']
    search_fields = ['title', 'body']
    ordering_fields = ['created_at', 'views', 'likes']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StoryCreateUpdateSerializer
        return StorySerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        story = self.get_object()
        user = request.user
        
        if story.likes.filter(id=user.id).exists():
            story.likes.remove(user)
            return Response({'status': 'unliked'})
        else:
            story.likes.add(user)
            return Response({'status': 'liked'})
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        # Get trending stories based on views and likes in the last 30 days
        from django.utils import timezone
        from datetime import timedelta
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        trending_stories = Story.objects.filter(
            created_at__gte=thirty_days_ago
        ).annotate(
            like_count=Count('likes'),
            comment_count=Count('comments')
        ).order_by('-views', '-like_count', '-comment_count')[:10]
        
        serializer = self.get_serializer(trending_stories, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(parent=None)  # Only top-level comments
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
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
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        queryset = Comment.objects.filter(parent=None)  # Only top-level comments
        
        # Filter by story if provided
        story_id = self.request.query_params.get('story', None)
        if story_id:
            queryset = queryset.filter(story_id=story_id)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
