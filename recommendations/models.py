from django.db import models
from django.conf import settings
from music.models import Songs  
from django.utils import timezone




class RecommendationCache(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='song_recommendations'
    )
    song = models.ForeignKey(Songs, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=["user", "-score"]),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.song.title} ({self.score:.2f})"