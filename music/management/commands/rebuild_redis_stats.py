from django.core.management.base import BaseCommand
from django.utils import timezone
from django_redis import get_redis_connection

from music.models import Songs, SongListen
from artists.models import Artist


class Command(BaseCommand):
    help = "Rebuild Redis statistics from PostgreSQL"

    def handle(self, *args, **options):
        redis = get_redis_connection("default")

        now = timezone.now()
        now_timestamp = now.timestamp()

        month_since = now - timezone.timedelta(days=30)
        twenty_four_hours_ago = now - timezone.timedelta(hours=24)

        self.stdout.write("Clearing old Redis statistics...")

        # ---------------------------------------------------------
        # Clear existing statistic keys
        # ---------------------------------------------------------

        for key in redis.scan_iter(match="song:*:plays:24h"):
            redis.delete(key)

        for key in redis.scan_iter(match="song:*:unique:listeners"):
            redis.delete(key)

        for key in redis.scan_iter(match="artist:*:monthly:listeners"):
            redis.delete(key)

        # ---------------------------------------------------------
        # Rebuild Song statistics
        # ---------------------------------------------------------

        songs = Songs.objects.all()

        for song in songs:

            # -----------------------------------------------------
            # Plays in last 24 hours
            # -----------------------------------------------------

            listens_24h = (
                SongListen.objects
                .filter(
                    song=song,
                    created_at__gte=twenty_four_hours_ago
                )
                .values_list("id", "created_at")
            )

            plays_key = f"song:{song.id}:plays:24h"

            plays_mapping = {
                str(listen_id): created_at.timestamp()
                for listen_id, created_at in listens_24h
            }

            if plays_mapping:
                redis.zadd(
                    plays_key,
                    plays_mapping
                )

            plays_24h = len(plays_mapping)

            # -----------------------------------------------------
            # Unique listeners - ALL TIME
            # -----------------------------------------------------

            unique_users = (
                SongListen.objects
                .filter(
                    song=song,
                    user__isnull=False
                )
                .values_list("user_id", flat=True)
                .distinct()
            )

            unique_key = (
                f"song:{song.id}:unique:listeners"
            )

            unique_users = list(unique_users)

            if unique_users:
                redis.sadd(
                    unique_key,
                    *[str(user_id) for user_id in unique_users]
                )

            unique_count = len(unique_users)

            # -----------------------------------------------------
            # Update PostgreSQL
            # -----------------------------------------------------

            Songs.objects.filter(
                id=song.id
            ).update(
                plays_last_24h=plays_24h,
                unique_listeners=unique_count,
            )

        # ---------------------------------------------------------
        # Rebuild Artist monthly listeners
        # ---------------------------------------------------------

        artists = Artist.objects.all()

        for artist in artists:

            artist_key = (
                f"artist:{artist.id}:monthly:listeners"
            )

            monthly_users = (
                SongListen.objects
                .filter(
                    song__artist=artist,
                    created_at__gte=month_since,
                    user__isnull=False
                )
                .values_list("user_id", flat=True)
                .distinct()
            )

            monthly_users = list(monthly_users)

            if monthly_users:
                redis.zadd(
                    artist_key,
                    {
                        str(user_id): now_timestamp
                        for user_id in monthly_users
                    }
                )

            monthly_count = len(monthly_users)

            Artist.objects.filter(
                id=artist.id
            ).update(
                monthly_listeners=monthly_count
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Redis statistics rebuilt successfully."
            )
        )
