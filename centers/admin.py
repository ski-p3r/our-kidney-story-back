from django.contrib import admin
from .models import DialysisCenter

@admin.register(DialysisCenter)
class DialysisCenterAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'city', 'state', 'type', 'contact', 'email', 'created_at'
    )
    list_filter = ('type', 'state', 'city')
    search_fields = ('name', 'city', 'state', 'contact', 'email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': (
                'name', 'type', 'description',
                'address', 'city', 'state',
                'contact', 'email', 'website', 'image_url'
            )
        }),
        ('Location Coordinates', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
