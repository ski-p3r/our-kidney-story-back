from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from .models import Feedback, FeedbackResponse
from .serializers import (
    FeedbackSerializer, 
    FeedbackCreateSerializer, 
    FeedbackUpdateStatusSerializer,
    FeedbackResponseSerializer
)
from core.permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin, IsAdminUser

class FeedbackRateThrottle(UserRateThrottle):
    rate = '10/day'

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'status', 'user']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    throttle_classes = [FeedbackRateThrottle]
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        elif self.action == 'update_status':
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FeedbackCreateSerializer
        elif self.action == 'update_status':
            return FeedbackUpdateStatusSerializer
        return FeedbackSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Feedback.objects.all()
        return Feedback.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        feedback = self.get_object()
        serializer = self.get_serializer(feedback, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(FeedbackSerializer(feedback).data)

class FeedbackResponseViewSet(viewsets.ModelViewSet):
    queryset = FeedbackResponse.objects.all()
    serializer_class = FeedbackResponseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['feedback', 'user']
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
