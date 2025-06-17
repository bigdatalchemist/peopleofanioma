from django.contrib import admin
from .models import Blog, Author, Tag, Reaction, Comment

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
