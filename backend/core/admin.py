from django.contrib import admin
from .models import (SearchQuery, Category, Topic, Source,
                     Content, Bookmark, Feedback, FlaggedContent,
                     UserSession, Recommendation)

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("user", "query_text", "category", "created_at", "status")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_name", "created_at")

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("topic_name", "category", "created_at")

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("source_name",)

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "created_at")

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "content", "created_at")

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "content", "rating", "created_at")

@admin.register(FlaggedContent)
class FlaggedContentAdmin(admin.ModelAdmin):
    list_display = ("user", "content", "status", "created_at")

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "last_login")

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("user", "content", "shown_at")