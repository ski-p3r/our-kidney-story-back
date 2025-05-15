from rest_framework import serializers
from .models import ForumCategory, ForumThread, ForumPost, ReportedContent
from users.serializers import UserSerializer

class ForumCategorySerializer(serializers.ModelSerializer):
    thread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumCategory
        fields = ['id', 'name', 'description', 'thread_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_thread_count(self, obj):
        return obj.threads.count()

class ForumPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumPost
        fields = ['id', 'thread', 'user', 'content', 'parent', 'created_at', 'updated_at', 'replies']
        read_only_fields = ['id', 'created_at', 'updated_at', 'replies']
    
    def get_replies(self, obj):
        if not obj.replies.exists():
            return []
        return ForumPostSerializer(obj.replies.all(), many=True).data

class ForumPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumPost
        fields = ['thread', 'content', 'parent']

class ForumThreadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = ForumCategorySerializer(read_only=True)
    post_count = serializers.SerializerMethodField()
    last_post = serializers.SerializerMethodField()
    
    class Meta:
        model = ForumThread
        fields = ['id', 'title', 'category', 'user', 'is_pinned', 'is_closed', 
                  'views', 'post_count', 'last_post', 'created_at', 'updated_at']
        read_only_fields = ['id', 'views', 'created_at', 'updated_at']
    
    def get_post_count(self, obj):
        return obj.posts.count()
    
    def get_last_post(self, obj):
        last_post = obj.posts.order_by('-created_at').first()
        if last_post:
            return {
                'id': last_post.id,
                'user': {
                    'id': last_post.user.id,
                    'full_name': last_post.user.get_full_name(),
                    'avatar_url': last_post.user.avatar_url
                },
                'created_at': last_post.created_at
            }
        return None

class ForumThreadCreateUpdateSerializer(serializers.ModelSerializer):
    first_post = serializers.CharField(write_only=True)
    
    class Meta:
        model = ForumThread
        fields = ['title', 'category', 'first_post']
    
    def create(self, validated_data):
        first_post_content = validated_data.pop('first_post')
        thread = ForumThread.objects.create(user=self.context['request'].user, **validated_data)
        
        # Create the first post
        ForumPost.objects.create(
            thread=thread,
            user=self.context['request'].user,
            content=first_post_content
        )
        
        return thread

class ForumThreadDetailSerializer(ForumThreadSerializer):
    posts = serializers.SerializerMethodField()
    
    class Meta(ForumThreadSerializer.Meta):
        fields = ForumThreadSerializer.Meta.fields + ['posts']
    
    def get_posts(self, obj):
        # Only get top-level posts
        posts = obj.posts.filter(parent=None)
        return ForumPostSerializer(posts, many=True, context=self.context).data

class ReportedContentSerializer(serializers.ModelSerializer):
    reported_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ReportedContent
        fields = ['id', 'content_type', 'content_id', 'reported_by', 'reason', 
                  'description', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

class ReportedContentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedContent
        fields = ['content_type', 'content_id', 'reason', 'description']
