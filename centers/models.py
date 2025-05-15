from django.db import models
from core.models import TimeStampedModel

class DialysisCenter(TimeStampedModel):
    CENTER_TYPES = (
        ('HOSPITAL', 'Hospital'),
        ('STANDALONE', 'Standalone'),
    )
    
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    type = models.CharField(max_length=10, choices=CENTER_TYPES)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
