from music.models import Songs, Album
from django.db.models import F, FloatField, ExpressionWrapper


def get_ranked_artist_songs(artistname):
    """
    Spotify-like ranking:
    priority:
    - recent plays
    - total play count
    - popularity
    - freshness
    """

    ranking_score = ExpressionWrapper(
        (
            F("plays_last_24h") * 0.5 +
            F("play_count") * 0.3 +
            F("popularity") * 0.2
        ),
        output_field=FloatField()
    )

    return (
        Songs.objects
        .filter(
            artist__artistname=artistname,
            is_published=True
        )
        .annotate(score=ranking_score)
        .select_related("album", "genre")
        .prefetch_related("artist")
        .order_by("-score", "-release_date")
        .distinct()
    )


def get_ranked_artist_albums(artistname):

    return (
        Album.objects
        .filter(
            artist__artistname=artistname,
            is_published=True
        )
        .select_related("artist")
        .order_by("-release_date")
    )
