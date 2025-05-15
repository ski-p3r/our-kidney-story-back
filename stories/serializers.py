from rest_framework import serializers
from .models import Story, Comment, Tag
from users.serializers import UserSerializer

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'story', 'user', 'content', 'parent', 'created_at', 'replies']
        read_only_fields = ['id', 'created_at', 'replies']
    
    def get_replies(self, obj):
        if not obj.replies.exists():
            return []
        return CommentSerializer(obj.replies.all(), many=True).data

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['story', 'content', 'parent']

class StorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)  # Changed this line
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ['id', 'title', 'body', 'image_url', 'user', 'tags', 'like_count', 
                  'is_liked', 'views', 'comment_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'views', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_comment_count(self, obj):
        return obj.comments.count()

class StoryCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False
    )
    
    class Meta:
        model = Story
        fields = ['title', 'body', 'image_url', 'tags']
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        story = Story.objects.create(user=self.context['request'].user, **validated_data)
        
        # Process tags
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
            story.tags.add(tag)
        
        return story
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        
        # Update story fields
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
    
    def to_representation(self, instance):
        # Use the StorySerializer for the output representation
        return StorySerializer(instance, context=self.context).data
