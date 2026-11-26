import random
from typing import Iterable, List
from music.models import Songs, SongListen, LikedSong


def _get_genre_candidates(current_playlist_songs: Iterable[Songs]) -> List[Songs]:
    """
    آهنگ‌هایی با ژانر مشابه آهنگ‌های پلی‌لیست
    """

    genres = [s.genre_id for s in current_playlist_songs if s.genre_id]

    if not genres:
        return []

    return list(
        Songs.objects.filter(
            genre_id__in=genres,
            is_published=True
        ).distinct()
    )


def _get_artist_candidates(current_playlist_songs: Iterable[Songs]) -> List[Songs]:
    """
    آهنگ‌هایی از همان آرتیست‌ها
    """

    artist_ids = set()

    for song in current_playlist_songs:
        artist_ids.update(a.id for a in song.artist.all())

    if not artist_ids:
        return []

    return list(
        Songs.objects.filter(
            artist__in=artist_ids,
            is_published=True
        ).distinct()
    )


def _get_user_personal_candidates(user) -> List[Songs]:
    """
    آهنگ‌هایی که کاربر لایک کرده یا زیاد گوش داده
    """

    liked_song_ids = list(
        LikedSong.objects.filter(user=user)
        .values_list("song_id", flat=True)
    )

    listened_song_ids = list(
        SongListen.objects.filter(user=user)
        .order_by("-seconds_listened")
        .values_list("song_id", flat=True)[:100]
    )

    candidate_ids = set(liked_song_ids) | set(listened_song_ids)

    if not candidate_ids:
        return []

    return list(
        Songs.objects.filter(
            id__in=candidate_ids,
            is_published=True
        )
    )


def suggest_songs_for_playlist(
    user,
    current_playlist_songs: Iterable[Songs],
    limit: int = 10
) -> List[Songs]:
    """
    الگوریتم پیشنهاد آهنگ برای افزودن به پلی‌لیست

    فاکتورها:
    - ژانر مشابه
    - آرتیست مشابه
    - سلیقه شخصی کاربر
    - حذف آهنگ‌های موجود در پلی‌لیست
    """

    current_playlist_songs = list(current_playlist_songs)

    # اگر پلی‌لیست خالی باشد
    if not current_playlist_songs:

        personal_candidates = _get_user_personal_candidates(user)

        if personal_candidates:
            random.shuffle(personal_candidates)
            return personal_candidates[:limit]

        return list(
            Songs.objects.filter(is_published=True)
            .order_by("-release_date")[:limit]
        )

    exclude_unique_ids = {s.unique_id for s in current_playlist_songs}

    genre_candidates = _get_genre_candidates(current_playlist_songs)

    artist_candidates = _get_artist_candidates(current_playlist_songs)

    personal_candidates = _get_user_personal_candidates(user)

    all_candidates = list(
        set(genre_candidates) |
        set(artist_candidates) |
        set(personal_candidates)
    )

    # حذف آهنگ‌هایی که در پلی‌لیست هستند
    all_candidates = [
        s for s in all_candidates
        if s.unique_id not in exclude_unique_ids
    ]

    random.shuffle(all_candidates)

    return all_candidates[:limit]
