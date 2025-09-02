from django.contrib import admin
from .models import Blog, Author, Tag, Reaction, Comment, VideoPost, VideoCategory

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'published', 'created_at')
    list_filter = ('category','published', 'created_at', 'tags')
    search_fields = ('title', 'category' ,'content', 'author__name')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Author)
admin.site.register(Tag)
admin.site.register(Reaction)
admin.site.register(Comment)


@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

@admin.register(VideoPost)
class VideoPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "is_featured", "published_at", "views")
    list_filter = ("is_published", "is_featured", "category", "created_at")
    search_fields = ("title", "description", "slug")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("category",)
