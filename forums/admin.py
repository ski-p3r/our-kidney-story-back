from django.contrib import admin
from .models import ForumCategory, ForumThread, ForumPost, ReportedContent

@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'user', 'is_pinned', 'is_closed', 'views', 'created_at')
    list_filter = ('is_pinned', 'is_closed', 'category')
    search_fields = ('title', 'user__first_name', 'user__last_name', 'category__name')
    autocomplete_fields = ('user', 'category')
    readonly_fields = ('views', 'created_at', 'updated_at')

@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'user', 'short_content', 'parent', 'created_at')
    search_fields = ('content', 'user__first_name', 'user__last_name', 'thread__title')
    autocomplete_fields = ('user', 'thread', 'parent')
    readonly_fields = ('created_at', 'updated_at')

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content Preview'

@admin.register(ReportedContent)
class ReportedContentAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'content_id', 'reported_by', 'reason', 'status', 'created_at')
    list_filter = ('content_type', 'reason', 'status')
    search_fields = ('reported_by__first_name', 'reported_by__last_name', 'description')
    autocomplete_fields = ('reported_by',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('content_type', 'content_id', 'reason', 'description', 'status', 'reported_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
