from django.contrib import admin
from .models import SearchQuery

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("user", "query_text", "category", "created_at", "status")
    search_fields = ("query_text", "category", "user__username")
