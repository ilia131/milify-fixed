import numpy as np
from django.utils import timezone
from math import log

def build_features(user, song):

    now = timezone.now()

    days_old = (now - song.release_date).days if song.release_date else 365

    freshness = np.exp(-days_old / 10)

    total_seconds = song.total_listen_time or 0
    listeners = song.unique_listeners or 0
    plays_24h = song.plays_last_24h or 0

    popularity = log(total_seconds + 1)
    engagement = log(listeners + 1)
    velocity = log(plays_24h + 1)

    genre_match = 0
    artist_match = 0

    if user and user.is_authenticated:

        if hasattr(user, "favorite_genres"):
            user_genres = set(user.favorite_genres.values_list("id", flat=True))
            if song.genre_id in user_genres:
                genre_match = 1

        if hasattr(song, "artist") and hasattr(user, "favorite_artists"):
            fav = set(user.favorite_artists.values_list("artistname", flat=True))
            if song.artist and song.artist.name in fav:
                artist_match = 1

    return np.array([
        freshness,
        popularity,
        engagement,
        velocity,
        genre_match,
        artist_match
    ])
