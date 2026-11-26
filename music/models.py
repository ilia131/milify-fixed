from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from artists.models import Artist
from django.contrib.postgres.indexes import GinIndex


class Album(models.Model):

    title = models.CharField(max_length=200)

    artist = models.ForeignKey(
        "artists.Artist",
        on_delete=models.CASCADE,
        related_name="albums"
    )

    cover = models.ImageField(upload_to="albums/", blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    release_date = models.DateField(default=timezone.now)

    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-release_date"]

    def __str__(self):
        return f"{self.title} - {self.artist}"
    
   

class AlbumArtist(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE )
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, default="main")






class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)



class MusicCategory(models.TextChoices):
    GAMING = "GAMING", "Gaming"
    DRIVING = "DRIVING", "Driving"
    GYM = "GYM", "Gym"
    STUDY = "STUDY", "Study"
    SLEEP = "SLEEP", "Sleep"
    PARTY = "PARTY", "Party"
    CHILL = "CHILL", "Chill"
    NIGHT_DRIVE = "NIGHT_DRIVE", "Night Drive"

class Songs(models.Model):
    artist = models.ManyToManyField(
        "artists.Artist",
        through="TrackArtist",
        related_name="tracks"
    )
    duration = models.PositiveIntegerField(
    default=0,
    help_text="Song duration in seconds",
)
 
    popularity = models.FloatField(default=0)
    tempo = models.FloatField(default=120)
    energy = models.FloatField(default=0.5)
    danceability = models.FloatField(default=0.5)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    loudness = models.FloatField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    category = models.CharField(
    max_length=30,
    choices=MusicCategory.choices,
    blank=True,
    null=True,
)
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    track = models.FileField(upload_to='music/', blank=True, null=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    plays_last_24h = models.IntegerField(default=0)
    
    unique_listeners = models.PositiveIntegerField(default=0)
   
    valence = models.FloatField(null=True, blank=True)        # ✅ ADD
    acousticness = models.FloatField(null=True, blank=True) 
    
    release_date = models.DateTimeField(default=timezone.now, db_index=True)
    
    play_count = models.PositiveIntegerField(default=0)
    total_listen_time = models.PositiveIntegerField(default=0)
    
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        related_name="songs"
    )    
    is_published = models.BooleanField(default=True)
    album = models.ForeignKey(
            "Album",
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name="tracks"
     )

    track_number = models.PositiveIntegerField(null=True, blank=True)
    audio_features = models.JSONField(default=dict, blank=True)
     
    class Meta:
        indexes = [
            GinIndex(
                    fields=["title"],
                    name="song_title_trgm",
                    opclasses=["gin_trgm_ops"],
                ),            
            models.Index(fields=["release_date"]),
            models.Index(fields=["play_count"]),
        ]
        
    

    def __str__(self):
        artists = ", ".join([a.artistname for a in self.artist.all()])
        return f"{self.title} - {artists}"

    def get_image_url(self):
        if self.image:
            return self.image.url
        return ""

    def get_track_url(self):
        if self.track:
            return self.track.url
        return ""



    def add_play(self, seconds: int = 0):
        self.play_count += 1
        self.total_listen_time += seconds
        self.save(update_fields=['play_count', 'total_listen_time'])
        
    
    def get_artists(self):
     return [rel.artist for rel in self.trackartist_set.all()]
    
    def __str__(self):
        artist_names = ", ".join([str(a) for a in self.get_artists()])
        return f"{self.title} - {artist_names}"
    
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    #     if self.album and self.album.artist:
    #         TrackArtist.objects.get_or_create(
    #             track=self,
    #             artist=self.album.artist,
    #             defaults={"role": "main"}
    #         )


class UserPlayHistory(models.Model):
    user_id = models.CharField(max_length=64)
    song = models.ForeignKey(Songs, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=30)
    skipped = models.BooleanField(default=False)



class UserFavoriteArtist(models.Model):
    user_id = models.CharField(max_length=64)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)


class Playlist(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.SET_NULL,
            null=True,
            blank=True
        )
    
    def __str__(self):
        return self.name


class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Songs, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    position = models.IntegerField(null=True, blank=True) 
     


class Lyrics(models.Model):
    song = models.ForeignKey(Songs, on_delete=models.CASCADE, related_name="lyrics_lines")
    time = models.FloatField()
    line = models.TextField()
    
    class Meta:
        ordering = ["time"]

class TrackArtist(models.Model):

    ROLE_CHOICES = [
        ("main", "Main Artist"),
        ("feature", "Featured Artist"),
        ("producer", "Producer"),
    ]

    track = models.ForeignKey(
        Songs,
        on_delete=models.CASCADE,
        
    )

    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="main"
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("track", "artist")
        ordering = ["order"]

    def __str__(self):
      return f"{self.artist.artistname} - {self.track.title} ({self.role})"



class SongListen(models.Model):

    song = models.ForeignKey(
        Songs,
        on_delete=models.CASCADE,
        related_name="listens"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    session_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )
    play_counted = models.BooleanField(default=False)
    completion_counted = models.BooleanField(
    default=False,
)
    interaction_seconds_recorded = models.PositiveIntegerField(
            default=0,
            help_text="Seconds already aggregated into UserSongInteraction",
        )
    skip_counted = models.BooleanField(
    default=False,
    help_text="Whether this session has already been counted as a skip",
)

    seconds_listened = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["song", "created_at"]),
            models.Index(fields=["session_id"]),
        ]




class ShortVideo(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True, null=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="short_videos"
    )

    main_artist = models.ForeignKey(
        Artist,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="main_short_videos"
    )

    featured_artists = models.ManyToManyField(
        Artist,
        related_name="featured_in_shorts",
        blank=True
    )

    audio_track = models.ForeignKey(
        Songs,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="short_videos"
    )

    video = models.FileField(upload_to="shorts/videos/")
    thumbnail = models.ImageField(upload_to="shorts/thumbnails/", blank=True, null=True)
    thumbnail_auto_generated = models.BooleanField(default=False)

    caption = models.TextField(blank=True, null=True)

    duration = models.FloatField(default=0)
    views = models.PositiveIntegerField(default=0)
    is_official = models.BooleanField(default=False)

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_shorts",
        blank=True
    )
    watch_time = models.BigIntegerField(default=0)

    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)

    allow_comments = models.BooleanField(default=True)
    score = models.FloatField(default=0, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["views"]),
            models.Index(fields=["-created_at", "views"]),
        ]

    def save(self, *args, **kwargs):
        # اگر یوزر آرتیست بود main_artist اتوماتیک ست شود
        if not self.main_artist:
            try:
                self.main_artist = self.user.artist_profile
            except Artist.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        if self.main_artist:
            return f"{self.main_artist.artistname} - Short {self.id}"
        return f"{self.user.username} - Short {self.id}"

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def increment_comments(self):
        self.comments_count += 1
        self.save(update_fields=['comments_count'])

    def increment_shares(self):
        self.shares_count += 1
        self.save(update_fields=['shares_count'])
    
    
    def add_watch_time(self, seconds):
        self.watch_time += seconds
        self.save(update_fields=["watch_time"])
        
        



class LikedSong(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="liked_songs"
    )

    song = models.ForeignKey(
        Songs,
        on_delete=models.CASCADE,
        related_name="liked_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "song")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ❤️ {self.song}"
    
    
    
class UserSongInteraction(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="song_interactions",
        db_index=True,
    )

    song = models.ForeignKey(
        Songs,
        on_delete=models.CASCADE,
        related_name="user_interactions",
        db_index=True,
    )

    # آخرین / مجموع رفتار کاربر با آهنگ
    play_count = models.PositiveIntegerField(default=0)

    total_listen_time = models.PositiveIntegerField(
        default=0,
        help_text="Total listening time in seconds",
    )

    skip_count = models.PositiveIntegerField(default=0)

    completed_count = models.PositiveIntegerField(default=0)

    replay_count = models.PositiveIntegerField(default=0)

    liked = models.BooleanField(default=False)

    favorited = models.BooleanField(default=False)

    # آخرین session
    last_session_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    # آخرین جایی که آهنگ از آنجا پخش شده
    last_source = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    # -------------------------
    # ML features
    # -------------------------

    avg_listen_time = models.FloatField(
        default=0
    )
    last_listen_duration = models.PositiveIntegerField(
        default=0,
        help_text="Duration of the latest listening session",
    )

    skip_rate = models.FloatField(
        default=0
    )

    completion_rate = models.FloatField(
        default=0
    )

    engagement_score = models.FloatField(
        default=0
    )

    # -------------------------
    # timestamps
    # -------------------------

    first_interaction_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    last_interaction_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    class Meta:
        ordering = ["-last_interaction_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "song"],
                name="unique_user_song_interaction",
            )
        ]

        indexes = [
            models.Index(
                fields=["user", "song"]
            ),
            models.Index(
                fields=["user", "last_interaction_at"]
            ),
            models.Index(
                fields=["song", "last_interaction_at"]
            ),
        ]

    def update_from_listen(
    self,
    duration=0,
    skipped=False,
    completed=False,
    session_id=None,
    source="",
):
        self.play_count += 1

        self.total_listen_time += duration

        self.last_listen_duration = duration

        if skipped:
            self.skip_count += 1

        if completed:
            self.completed_count += 1

        # -------------------------
        # Aggregate ML features
        # -------------------------

        if self.play_count > 0:

            self.avg_listen_time = (
                self.total_listen_time /
                self.play_count
            )

            self.skip_rate = (
                self.skip_count /
                self.play_count
            )

            self.completion_rate = (
                self.completed_count /
                self.play_count
            )

        # -------------------------
        # Last interaction
        # -------------------------

        self.last_session_id = session_id

        self.last_source = source

        self.last_interaction_at = timezone.now()

        # -------------------------
        # Engagement score
        # -------------------------

        self.engagement_score = (
            self.avg_listen_time * 0.4
            + self.completion_rate * 30
            + self.play_count * 2
            + self.replay_count * 3
            + (5 if self.liked else 0)
            + (5 if self.favorited else 0)
            - self.skip_rate * 10
        )

        self.save()
        
        

class ShortVideoComment(models.Model):
    short_video = models.ForeignKey(
        ShortVideo,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="short_video_comments",
    )

    text = models.TextField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # برای کامنت‌های تو در تو مثل Instagram
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_short_video_comments",
        blank=True,
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["short_video", "created_at"]
            ),
            models.Index(
                fields=["user", "created_at"]
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.short_video_id}"