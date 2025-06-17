from django.contrib import admin
from .models import DiasporaEntry

@admin.register(DiasporaEntry)
class DiasporaEntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'city', 'profession', 'year_migrated', 'timestamp', 'local_origin')
    search_fields = ('name', 'country', 'city', 'profession', 'local_origin')
