from music.models import Songs, LikedSong, SongListen
from django.db.models import Count, Q


def get_user_recommendations(user, limit=20):

    liked_song_ids = LikedSong.objects.filter(user=user).values_list("song_id", flat=True)

    listened_song_ids = SongListen.objects.filter(user=user)\
        .values_list("song_id", flat=True)

    base_song_ids = set(list(liked_song_ids) + list(listened_song_ids))

    if not base_song_ids:
        return Songs.objects.order_by("-play_count")[:limit]

    base_songs = Songs.objects.filter(id__in=base_song_ids)

    genres = base_songs.values_list("genre", flat=True)

    artists = base_songs.values_list("trackartist__artist", flat=True)

    recommendations = Songs.objects.filter(
        Q(genre__in=genres) |
        Q(trackartist__artist__in=artists)
    ).exclude(
        id__in=base_song_ids
    ).annotate(
        popularity=Count("liked_by")
    ).order_by(
        "-popularity",
        "-play_count"
    ).distinct()[:limit]

    return recommendations
