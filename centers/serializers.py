from rest_framework import serializers
from .models import DialysisCenter

class DialysisCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DialysisCenter
        fields = ['id', 'name', 'address', 'city', 'state', 'contact', 'email', 
                  'website', 'type', 'description', 'image_url', 'latitude', 
                  'longitude', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
