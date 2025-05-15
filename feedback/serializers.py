from rest_framework import serializers
from .models import Feedback, FeedbackResponse
from users.serializers import UserSerializer

class FeedbackResponseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = FeedbackResponse
        fields = ['id', 'feedback', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class FeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    responses = FeedbackResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'title', 'description', 'type', 'status', 'user', 'responses', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['title', 'description', 'type']

class FeedbackUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['status']
