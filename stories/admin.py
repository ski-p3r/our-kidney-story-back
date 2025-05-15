from django.contrib import admin
from .models import Tag, Story, Comment

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ('user', 'content', 'parent', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'views', 'like_count', 'created_at')
    search_fields = ('title', 'body', 'user__email')
    list_filter = ('created_at',)
    filter_horizontal = ('tags', 'likes')
    inlines = [CommentInline]
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('story', 'user', 'content', 'parent', 'created_at')
    search_fields = ('story__title', 'user__email', 'content')
    list_filter = ('created_at',)
    ordering = ('created_at',)
