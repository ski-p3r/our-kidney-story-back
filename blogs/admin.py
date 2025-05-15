from django.contrib import admin
from .models import Blog, BlogComment

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published', 'views', 'created_at')
    list_filter = ('published', 'author', 'tags')
    search_fields = ('title', 'content', 'author__first_name', 'author__last_name')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('author', 'tags')
    readonly_fields = ('views', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'thumbnail_url', 'author', 'tags', 'published')
        }),
        ('Metadata', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'content_short', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__first_name', 'user__last_name', 'content', 'blog__title')
    autocomplete_fields = ('user', 'blog', 'parent')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def content_short(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Comment'
