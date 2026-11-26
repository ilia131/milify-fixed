from datetime import timedelta
from django.utils import timezone
from django.db.models import Count

from music.models import Songs, SongListen

from django.db.models import Count

def update_plays_last_24h():

    since = timezone.now() - timedelta(hours=24)

    Songs.objects.update(plays_last_24h=0)

    data = (
        SongListen.objects
        .filter(created_at__gte=since)
        .values("song")
        .annotate(c=Count("id"))
    )

    for row in data:
        Songs.objects.filter(id=row["song"]).update(
            plays_last_24h=row["c"]
        )



def update_unique_listeners():

    data = (
        SongListen.objects
        .values("song")
        .annotate(c=Count("user", distinct=True))
    )

    for row in data:
        Songs.objects.filter(id=row["song"]).update(
            unique_listeners=row["c"]
        )



