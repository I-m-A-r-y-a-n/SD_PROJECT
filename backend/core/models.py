# from django.db import models
# from django.contrib.auth.models import User

# class SearchQuery(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     query_text = models.TextField()

#     answer_text = models.TextField(null=True, blank=True)   # NEW FIELD

#     category = models.CharField(max_length=50)
#     created_at = models.DateTimeField(auto_now_add=True)
#     session_id = models.CharField(max_length=100)
#     is_followup = models.BooleanField(default=False)
#     source_used = models.CharField(max_length=50)
#     status = models.CharField(max_length=20, default="completed")

#     videos_json = models.TextField(null=True, blank=True)
#     links_json = models.TextField(null=True, blank=True)

#     def __str__(self):
#         return self.query_text[:50]

from django.db import models
from django.contrib.auth.models import User


# ── CATEGORY ──
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name


# ── TOPIC ──
class Topic(models.Model):
    topic_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic_name


# ── SOURCE ──
class Source(models.Model):
    source_name = models.CharField(max_length=100)

    def __str__(self):
        return self.source_name


# ── CONTENT ──
class Content(models.Model):
    title = models.CharField(max_length=300)
    url = models.URLField(max_length=500)
    snippet = models.TextField(null=True, blank=True)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title[:60]


# ── SEARCH ──
class SearchQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query_text = models.TextField()
    answer_text = models.TextField(null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100)
    is_followup = models.BooleanField(default=False)
    source_used = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="completed")
    videos_json = models.TextField(null=True, blank=True)
    links_json = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.query_text[:50]


# ── BOOKMARK ──
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.content.title[:40]}"


# ── FEEDBACK ──
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username}"


# ── FLAGGED CONTENT ──
class FlaggedContent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Flag by {self.user.username}"


# ── SESSION ──
class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session: {self.user.username}"


# ── RECOMMENDATION ──
class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    reason = models.TextField(null=True, blank=True)
    shown_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rec for {self.user.username}"