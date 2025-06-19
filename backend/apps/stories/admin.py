# stories/admin.py
from django.contrib import admin
from .models import Story

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'is_approved', 'date_submitted')
    list_filter = ('is_approved', 'title', 'author_name')
    search_fields = ('title', 'author_name')
    actions = ['approve_selected']

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)

