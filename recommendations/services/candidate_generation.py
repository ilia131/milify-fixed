from django.db.models import Q
from music.models import Songs, LikedSong, SongListen


def candidates_from_genre(current_songs, limit=200):
    genres = {s.genre_id for s in current_songs if s.genre_id}
    if not genres:
        return Songs.objects.none()
    return (
        Songs.objects.filter(is_published=True, genre_id__in=genres)
        .exclude(id__in=[s.id for s in current_songs])
        .order_by("-play_count")[:limit]
    )


def candidates_from_artists(current_songs, limit=200):
    artist_ids = set()
    for s in current_songs:
        artist_ids |= set(s.artist.values_list("id", flat=True))
    if not artist_ids:
        return Songs.objects.none()
    return (
        Songs.objects.filter(is_published=True, artist__id__in=artist_ids)
        .exclude(id__in=[s.id for s in current_songs])
        .distinct()
        .order_by("-play_count")[:limit]
    )


def candidates_from_user_history(user, limit=200):
    liked = Songs.objects.filter(liked_by__user=user).distinct()[:limit]
    listened = Songs.objects.filter(listens__user=user).distinct()[:limit]
    uniq = {s.id: s for s in (list(liked) + list(listened))}
    return list(uniq.values())


def candidates_from_trending(limit=200):
    return Songs.objects.filter(is_published=True).order_by("-play_count")[:limit]
