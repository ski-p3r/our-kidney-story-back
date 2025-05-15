from rest_framework import serializers
from .models import Blog, BlogComment
from users.serializers import UserSerializer
from stories.serializers import TagSerializer

class BlogCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogComment
        fields = ['id', 'blog', 'user', 'content', 'parent', 'created_at', 'replies']
        read_only_fields = ['id', 'created_at', 'replies']
    
    def get_replies(self, obj):
        if not obj.replies.exists():
            return []
        return BlogCommentSerializer(obj.replies.all(), many=True).data

class BlogCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = ['blog', 'content', 'parent']

class BlogSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'content', 'thumbnail_url', 'author', 
                  'tags', 'published', 'views', 'comment_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'views', 'created_at', 'updated_at']
    
    def get_comment_count(self, obj):
        return obj.comments.count()

class BlogCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False
    )
    
    class Meta:
        model = Blog
        fields = ['title', 'content', 'thumbnail_url', 'tags', 'published']
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        blog = Blog.objects.create(author=self.context['request'].user, **validated_data)
        
        # Process tags
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
            blog.tags.add(tag)
        
        return blog
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        
        # Update blog fields
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
