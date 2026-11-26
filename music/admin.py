from django.contrib import admin
from django.db import transaction

from .models import (
    Songs,
    TrackArtist,
    Genre,
    Album,
    Lyrics,
    ShortVideo,
    PlaylistTrack,
    Playlist,
    UserSongInteraction
)

from subscriptions.models import ArtistSubscriptionTrack


class TrackArtistInline(admin.TabularInline):
    model = TrackArtist
    extra = 1


class LyricsInline(admin.TabularInline):
    model = Lyrics
    extra = 1


class SongsInline(admin.TabularInline):
    model = Songs
    extra = 1


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "release_date")
    inlines = [SongsInline]


@admin.register(Songs)
class SongsAdmin(admin.ModelAdmin):
    inlines = [
        TrackArtistInline,
        LyricsInline,
    ]

    list_display = (
        "title",
        "release_date",
        "category",
        "play_count",
        "subscription_only",
    )

    list_filter = (
        "category",
        "release_date",
    )

    search_fields = (
        "title",
        "description",
    )

    @admin.display(
        boolean=True,
        description="Subscription Only",
    )
    def subscription_only(self, obj):
        artists_count = obj.artist.count()

        if artists_count == 0:
            return False

        approved_count = (
            obj.artist_subscription_access
            .filter(status="APPROVED")
            .count()
        )

        return approved_count == artists_count

    @admin.action(description="فعال کردن Subscription Only")
    def enable_subscription(self, request, queryset):

        with transaction.atomic():

            for song in queryset:

                artists = song.artist.all()

                for artist in artists:

                    ArtistSubscriptionTrack.objects.update_or_create(
                        artist=artist,
                        song=song,
                        defaults={
                            "status": "APPROVED",
                        },
                    )

        self.message_user(
            request,
            "Subscription Only برای آهنگ‌های انتخاب‌شده فعال شد.",
        )

    @admin.action(description="غیرفعال کردن Subscription Only")
    def disable_subscription(self, request, queryset):

        with transaction.atomic():

            for song in queryset:

                ArtistSubscriptionTrack.objects.filter(
                    song=song
                ).update(
                    status="REJECTED"
                )

        self.message_user(
            request,
            "Subscription Only برای آهنگ‌های انتخاب‌شده غیرفعال شد.",
        )

    actions = [
        "enable_subscription",
        "disable_subscription",
    ]

@admin.register(UserSongInteraction)
class UserSongInteractionAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "song",
        "play_count",
        "total_listen_time",
        "avg_listen_time",
        "skip_rate",
        "completion_rate",
        "engagement_score",
        "liked",
        "favorited",
        "last_source",
        "last_interaction_at",
    )

    list_filter = (
        "liked",
        "favorited",
        "last_source",
        "last_interaction_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "song__title",
    )

    readonly_fields = (
        "id",
        "avg_listen_time",
        "last_listen_duration",
        "skip_rate",
        "completion_rate",
        "engagement_score",
        "first_interaction_at",
        "last_interaction_at",
    )

    ordering = (
        "-engagement_score",
        "-last_interaction_at",
    )

    list_per_page = 50
admin.site.register(Genre)
admin.site.register(Playlist)
admin.site.register(PlaylistTrack)


@admin.register(ShortVideo)
class ShortVideoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "artist_display",
        "views",
        "likes_count",
        "is_official",
        "created_at",
    )

    list_filter = (
        "is_official",
        "created_at",
    )

    search_fields = (
        "user__username",
        "main_artist__artistname",
        "caption",
    )

    filter_horizontal = (
        "featured_artists",
        "likes",
    )

    def artist_display(self, obj):
        if obj.main_artist:
            return obj.main_artist.artistname

        if hasattr(obj.user, "artist_profile"):
            return obj.user.artist_profile.artistname

        return "Fan"

    artist_display.short_description = "Artist"

    def likes_count(self, obj):
        return obj.likes.count()

    likes_count.short_description = "Likes"