from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class ForumCategory(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Forum Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ForumThread(TimeStampedModel):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='threads')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_threads')
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title

class ForumPost(TimeStampedModel):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Post by {self.user.get_full_name()} in {self.thread.title}"

class ReportedContent(TimeStampedModel):
    CONTENT_TYPES = (
        ('THREAD', 'Thread'),
        ('POST', 'Post'),
    )
    
    REPORT_REASONS = (
        ('SPAM', 'Spam'),
        ('OFFENSIVE', 'Offensive Content'),
        ('INAPPROPRIATE', 'Inappropriate Content'),
        ('OTHER', 'Other'),
    )
    
    REPORT_STATUS = (
        ('PENDING', 'Pending'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    )
    
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    content_id = models.PositiveIntegerField()
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_content')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=REPORT_STATUS, default='PENDING')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report by {self.reported_by.get_full_name()} - {self.get_reason_display()}"
