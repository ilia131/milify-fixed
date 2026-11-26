from django.db import models
import uuid

from django.db import models

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.indexes import GinIndex


class ArtistPick(models.Model):
    artist = models.OneToOneField(
        "Artist",
        on_delete=models.CASCADE,
        related_name="artist_pick"
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")

    message = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.artist.artistname} - Pick"
    
    
    
class Artist(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False,   blank=True , unique=True)
     
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="artist_profile"
    )
    artistname= models.CharField(max_length=255 , unique=True , blank=True , null=True)
    bio = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    background = models.ImageField(
        upload_to='images/',
        null=True)
    monthly_listeners = models.PositiveBigIntegerField(default=0)
    youtube_embed = models.URLField(
    max_length=500,
    blank=True,
    null=True,
    help_text="YouTube embed URL"
)
    profile_pic = models.ImageField(
        upload_to='artists/',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            GinIndex(
                fields=["artistname"],
                name="artist_name_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def __str__(self):
        return self.artistname

    def get_image(self, request):
        if self.profile_pic:
            return request.build_absolute_uri(self.profile_pic.url)
        return ""

    def get_background(self, request):
        if self.background:
            return request.build_absolute_uri(self.background.url)
        return ""
    


class ArtistYouTubeVideo(models.Model):
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="youtube_videos",
    )

    title = models.CharField(
        max_length=255,
        blank=True,
    )

    embed_url = models.URLField(
        max_length=500,
    )

    thumbnail = models.URLField(
        max_length=500,
        blank=True,
        null=True,
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["order", "-created_at"]

        indexes = [
            models.Index(
                fields=["artist", "order"]
            ),
            models.Index(
                fields=["artist", "is_active"]
            ),
        ]

    def __str__(self):
        return f"{self.artist.artistname} - {self.title or 'YouTube Video'}"    
   
    # def __str__(self):
    #     return self.email


    # def views_count(self):
        
    #     return View1.objects.filter(views_count=self.pk)
    
    
    
    # def follow_count(self):
    #     return Follow.objects.filter(follow_count=self.pk)





class FollowArtist(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following_artists"
    )

    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="followers"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "artist"],
                name="unique_user_artist_follow"
            )
        ]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["artist"]),
        ]

    def __str__(self):
        return f"{self.user} -> {self.artist}"