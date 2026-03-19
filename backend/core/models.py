from django.db import models
from django.contrib.auth.models import User

class SearchQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query_text = models.TextField()

    answer_text = models.TextField(null=True, blank=True)   # NEW FIELD

    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100)
    is_followup = models.BooleanField(default=False)
    source_used = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="completed")

    def __str__(self):
        return self.query_text[:50]