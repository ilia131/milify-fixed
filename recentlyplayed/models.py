from django.db import models
from django.utils import timezone
from music.models import Songs 
from django.conf import settings

from django.db import models
from django.utils import timezone
from django.conf import settings
from music.models import Songs

class RecentlyPlayed(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recently_played"
    )

    song = models.ForeignKey(
        Songs,
        on_delete=models.CASCADE,
        related_name="recent_plays"
    )

    played_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-played_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "song"],
                name="unique_user_song_recent"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.song}"

