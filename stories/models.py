from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Tag(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Story(TimeStampedModel):
    title = models.CharField(max_length=255)
    body = models.TextField()
    image_url = models.URLField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories')
    tags = models.ManyToManyField(Tag, related_name='stories', blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_stories', blank=True)
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'Stories'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def like_count(self):
        return self.likes.count()

class Comment(TimeStampedModel):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='story_comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.get_full_name()} on {self.story.title}"
