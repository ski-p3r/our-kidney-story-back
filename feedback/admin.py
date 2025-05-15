# from django.db import models
# from django.conf import settings
# from core.models import TimeStampedModel

# class Feedback(TimeStampedModel):
#     FEEDBACK_TYPES = (
#         ('BUG', 'Bug'),
#         ('FEATURE', 'Feature Request'),
#         ('GENERAL', 'General Feedback'),
#     )
    
#     FEEDBACK_STATUS = (
#         ('PENDING', 'Pending'),
#         ('ACCEPTED', 'Accepted'),
#         ('DECLINED', 'Declined'),
#         ('IMPLEMENTED', 'Implemented'),
#     )
    
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     type = models.CharField(max_length=10, choices=FEEDBACK_TYPES)
#     status = models.CharField(max_length=15, choices=FEEDBACK_STATUS, default='PENDING')
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback')
    
#     class Meta:
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return self.title

# class FeedbackResponse(TimeStampedModel):
#     feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='responses')
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback_responses')
#     content = models.TextField()
    
#     class Meta:
#         ordering = ['created_at']
    
#     def __str__(self):
#         return f"Response to {self.feedback.title}"
