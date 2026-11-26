from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_redis import get_redis_connection

from music.models import Songs, SongListen
from artists.models import Artist


@receiver(post_save, sender=SongListen)
def update_song_stats_on_listen(
    sender,
    instance,
    created,
    **kwargs
):

    # ---------------------------------------------------------
    # Only process a real Play
    # ---------------------------------------------------------

    if not instance.play_counted:
        return

    redis = get_redis_connection("default")

    song = instance.song
    artists = song.artist.all()

    now = timezone.now()
    now_timestamp = now.timestamp()

    # ---------------------------------------------------------
    # Plays in last 24 hours
    # ---------------------------------------------------------

    plays_24h_key = f"song:{song.id}:plays:24h"

    redis.zadd(
        plays_24h_key,
        {
            str(instance.id): now_timestamp
        }
    )

    twenty_four_hours_ago = (
        now_timestamp - (24 * 60 * 60)
    )

    redis.zremrangebyscore(
        plays_24h_key,
        0,
        twenty_four_hours_ago
    )

    plays_24h = redis.zcard(
        plays_24h_key
    )

    # ---------------------------------------------------------
    # Unique listeners - ALL TIME
    # ---------------------------------------------------------

    unique_listeners_key = (
        f"song:{song.id}:unique:listeners"
    )

    if instance.user_id:

        redis.sadd(
            unique_listeners_key,
            str(instance.user_id)
        )

        unique_listeners = redis.scard(
            unique_listeners_key
        )

    else:

        unique_listeners = (
            SongListen.objects
            .filter(
                song=song,
                user__isnull=False,
                play_counted=True,
            )
            .values("user")
            .distinct()
            .count()
        )

    # ---------------------------------------------------------
    # Update Song statistics
    # ---------------------------------------------------------

    Songs.objects.filter(
        id=song.id
    ).update(
        plays_last_24h=plays_24h,
        unique_listeners=unique_listeners,
    )

    # ---------------------------------------------------------
    # Monthly listeners - LAST 30 DAYS
    # ---------------------------------------------------------

    month_since = (
        now - timezone.timedelta(days=30)
    )

    for artist in artists:

        if instance.user_id:

            artist_key = (
                f"artist:{artist.id}:monthly:listeners"
            )

            redis.zadd(
                artist_key,
                {
                    str(instance.user_id): now_timestamp
                }
            )

            month_ago_timestamp = (
                now_timestamp - (30 * 24 * 60 * 60)
            )

            redis.zremrangebyscore(
                artist_key,
                0,
                month_ago_timestamp
            )

            monthly_listeners = redis.zcard(
                artist_key
            )

        else:

            monthly_listeners = (
                SongListen.objects
                .filter(
                    song__artist=artist,
                    created_at__gte=month_since,
                    user__isnull=False,
                    play_counted=True,
                )
                .values("user")
                .distinct()
                .count()
            )

        # -----------------------------------------------------
        # Update Artist
        # -----------------------------------------------------

        Artist.objects.filter(
            id=artist.id
        ).update(
            monthly_listeners=monthly_listeners
        )