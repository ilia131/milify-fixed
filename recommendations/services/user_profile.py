import numpy as np
from datetime import timedelta
from django.utils import timezone
from music.models import SongListen, LikedSong
from .feature_extraction import song_embedding


def get_user_recent_songs(user):

    listens = (
        SongListen.objects
        .filter(user=user,
                created_at__gte=timezone.now() - timedelta(days=30))
        .select_related("song")
        .order_by("-created_at")[:100]
    )

    songs = [l.song for l in listens]

    if len(songs) < 20:

        likes = (
            LikedSong.objects
            .filter(user=user)
            .select_related("song")
            .order_by("-created_at")[:50]
        )

    if len(songs) < 20:
        likes = (
            LikedSong.objects
            .filter(user=user)
            .select_related("song")
            .order_by("-created_at")[:50]
        )
        songs += [l.song for l in likes]

    # حذف تکراری‌ها
    unique_songs = list({s.id: s for s in songs}.values())
    return unique_songs


def user_embedding(user) -> np.ndarray:
    from music.models import Songs  # برای مورد پیش‌فرض
    songs = get_user_recent_songs(user)
    if not songs:
        # fallback: آهنگ تصادفی تا سایز بردار را بدانیم
        dummy = Songs.objects.filter(is_published=True).first()
        if not dummy:
            return np.zeros(64, dtype=float)
        return np.zeros_like(song_embedding(dummy))
    embs = [song_embedding(s) for s in songs]
    return np.mean(embs, axis=0)




