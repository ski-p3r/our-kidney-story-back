from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import DialysisCenter
from .serializers import DialysisCenterSerializer
from core.permissions import IsAdminUser

class DialysisCenterViewSet(viewsets.ModelViewSet):
    queryset = DialysisCenter.objects.all()
    serializer_class = DialysisCenterSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city', 'state', 'type']
    search_fields = ['name', 'address', 'city', 'state']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
