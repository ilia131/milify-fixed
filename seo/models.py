from django.db import models


class SEOPage(models.Model):

    PAGE_TYPES = [
        ("HOME", "Home"),
        ("SONG", "Song"),
        ("ARTIST", "Artist"),
        ("ALBUM", "Album"),
        ("PLAYLIST", "Playlist"),
        ("GENRE", "Genre"),
        ("SEARCH", "Search"),
    ]

    page_type = models.CharField(
        max_length=20,
        choices=PAGE_TYPES,
    )

    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    keywords = models.TextField(
        blank=True,
    )

    canonical_url = models.URLField(
        blank=True,
    )

    og_title = models.CharField(
        max_length=255,
        blank=True,
    )

    og_description = models.TextField(
        blank=True,
    )

    og_image = models.URLField(
        blank=True,
    )

    twitter_title = models.CharField(
        max_length=255,
        blank=True,
    )

    twitter_description = models.TextField(
        blank=True,
    )

    twitter_image = models.URLField(
        blank=True,
    )

    robots = models.CharField(
        max_length=100,
        default="index, follow",
    )

    schema_type = models.CharField(
        max_length=100,
        blank=True,
    )

    schema_data = models.JSONField(
        default=dict,
        blank=True,
    )

    is_indexable = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "-updated_at"
        ]

        indexes = [
            models.Index(
                fields=[
                    "page_type",
                    "object_id",
                ]
            ),
        ]

    def __str__(self):

        return f"{self.page_type} - {self.slug}"





class ArtistSEO(models.Model):
    artist = models.OneToOneField(
        "artists.Artist",
        on_delete=models.CASCADE,
        related_name="seo",
    )

    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="SEO title. اگر خالی باشد از نام آرتیست ساخته می‌شود.",
    )

    description = models.TextField(
        blank=True,
        help_text="Meta description. اگر خالی باشد از bio آرتیست استفاده می‌شود.",
    )

    keywords = models.TextField(
        blank=True,
        help_text="کلمات کلیدی با کاما جدا شوند.",
    )

    canonical_url = models.URLField(
        blank=True,
    )

    og_title = models.CharField(
        max_length=255,
        blank=True,
    )

    og_description = models.TextField(
        blank=True,
    )

    og_image = models.URLField(
        blank=True,
    )

    twitter_title = models.CharField(
        max_length=255,
        blank=True,
    )

    twitter_description = models.TextField(
        blank=True,
    )

    twitter_image = models.URLField(
        blank=True,
    )

    robots = models.CharField(
        max_length=255,
        default="index, follow",
    )

    is_indexable = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"SEO - {self.artist.artistname}"
    
    
    
class SongSEO(models.Model):
    song = models.OneToOneField(
        "music.Songs",
        on_delete=models.CASCADE,
        related_name="seo",
    )

    title = models.CharField(
        max_length=255,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    keywords = models.TextField(
        blank=True,
        help_text="کلمات کلیدی با کاما جدا شوند.",
    )

    canonical_url = models.URLField(
        blank=True,
    )

    og_title = models.CharField(
        max_length=255,
        blank=True,
    )

    og_description = models.TextField(
        blank=True,
    )

    og_image = models.URLField(
        blank=True,
    )

    twitter_title = models.CharField(
        max_length=255,
        blank=True,
    )

    twitter_description = models.TextField(
        blank=True,
    )

    twitter_image = models.URLField(
        blank=True,
    )

    robots = models.CharField(
        max_length=255,
        default="index, follow",
    )

    is_indexable = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"SEO - {self.song.title}"
