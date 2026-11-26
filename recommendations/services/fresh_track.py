# from django.utils import timezone
# from datetime import timedelta
# from math import exp, log

# from music.models import Songs


# def get_fresh_tracks(user, limit=20):

#     now = timezone.now()
#     min_date = now - timedelta(days=30)

#     songs = (
#         Songs.objects.filter(
#             release_date__gte=min_date,
#             is_published=True
#         )
#         .select_related("genre")
#         .prefetch_related(
#             "trackartist_set",
#             "trackartist_set__artist",
#         )
#     )

#     user_genres = set()
#     user_artists = set()

#     if user and user.is_authenticated:

#         if hasattr(user, "favorite_genres"):
#             user_genres = set(user.favorite_genres.values_list("id", flat=True))

#         if hasattr(user, "favorite_artists"):
#             user_artists = set(
#                 user.favorite_artists.values_list("artistname", flat=True)
#             )

#     scored = []

#     for song in songs:

#         days_old = (now - song.release_date).days

#         freshness = exp(-days_old / 5)
#         freshness_score = freshness * 40

#         total_seconds = song.total_listen_time or 0
#         unique_listeners = song.unique_listeners or 0

#         engagement_raw = log(total_seconds + 1) + log(unique_listeners + 1)
#         engagement_score = min(engagement_raw * 3.5, 20)

#         plays_last_day = song.plays_last_24h or 0
#         velocity_score = min(log(plays_last_day + 1) * 6, 18)

#         popularity_score = min(log(total_seconds + 1) * 1.5, 12)

#         interest_score = 0

#         if song.genre_id in user_genres:
#             interest_score += 10

#         main_artist = None
#         relations = song.trackartist_set.all()

#         for rel in relations:
#             if rel.role == "main":
#                 main_artist = rel.artist
#                 break

#         if not main_artist and relations:
#             main_artist = relations[0].artist

#         artist_name = main_artist.artistname if main_artist else None

#         if artist_name in user_artists:
#             interest_score += 15

#         exploration_score = 0
#         if days_old <= 7:
#             if total_seconds < 50000 and unique_listeners < 30:
#                 exploration_score = 6

#         diversity_penalty = 0
#         if total_seconds > 3_000_000:
#             diversity_penalty = -8

#         noise = ((hash(song.id) % 100) / 100) * 0.8

#         score = (
#             freshness_score +
#             engagement_score * 0.5 +
#             velocity_score * 0.6 +
#             popularity_score +
#             interest_score +
#             exploration_score +
#             diversity_penalty +
#             noise
#         )

#         scored.append((score, song, artist_name))

#     scored.sort(key=lambda x: x[0], reverse=True)

#     result = []
#     artist_counter = {}

#     for score, song, artist_name in scored:

#         if not artist_name:
#             continue

#         count = artist_counter.get(artist_name, 0)

#         if count >= 2:
#             continue

#         result.append(song)
#         artist_counter[artist_name] = count + 1

#         if len(result) >= limit:
#             break

#     return result



import random

from math import exp, log
from datetime import timedelta

from django.utils import timezone

from music.models import Songs

from .redis_service import (
    get_song_plays_24h,
    get_song_unique_listeners,
)


def get_fresh_tracks(user, limit=20):

    now = timezone.now()
    min_date = now - timedelta(days=30)

    songs = (
        Songs.objects
        .filter(
            release_date__gte=min_date,
            is_published=True,
        )
        .select_related("genre")
        .prefetch_related(
            "trackartist_set",
            "trackartist_set__artist",
        )
    )

    user_genres = set()
    user_artists = set()

    if user and user.is_authenticated:

        if hasattr(user, "favorite_genres"):
            user_genres = set(
                user.favorite_genres.values_list(
                    "id",
                    flat=True,
                )
            )

        if hasattr(user, "favorite_artists"):
            user_artists = set(
                user.favorite_artists.values_list(
                    "artistname",
                    flat=True,
                )
            )

    scored = []

    for song in songs:

        if not song.release_date:
            continue

        days_old = max(
            0,
            (now - song.release_date).days,
        )

        # =====================================================
        # REAL-TIME REDIS STATS
        # =====================================================

        total_seconds = song.total_listen_time or 0

        try:
            unique_listeners = get_song_unique_listeners(song.id)
        except Exception:
            unique_listeners = song.unique_listeners or 0

        try:
            plays_last_day = get_song_plays_24h(song.id)
        except Exception:
            plays_last_day = song.plays_last_24h or 0

        # =====================================================
        # FRESHNESS
        # =====================================================

        freshness_score = (
            exp(-days_old / 5) * 45
        )

        # =====================================================
        # ENGAGEMENT
        # =====================================================

        engagement = (
            log(total_seconds + 1)
            +
            log(unique_listeners + 1)
        )

        engagement_score = min(
            engagement * 3.5,
            20,
        )

        # =====================================================
        # VELOCITY
        # =====================================================

        velocity_score = min(
            log(plays_last_day + 1) * 6,
            18,
        )

        # =====================================================
        # POPULARITY
        # =====================================================

        popularity_score = min(
            log(total_seconds + 1) * 1.5,
            12,
        )

        # =====================================================
        # USER INTEREST
        # =====================================================

        interest_score = 0

        if song.genre_id in user_genres:
            interest_score += 10

        # =====================================================
        # MAIN ARTIST
        # =====================================================

        main_artist = None

        for rel in song.trackartist_set.all():

            if rel.role == "main":
                main_artist = rel.artist
                break

        if not main_artist:

            relations = list(
                song.trackartist_set.all()
            )

            if relations:
                main_artist = relations[0].artist

        artist_name = (
            main_artist.artistname
            if main_artist
            else None
        )

        # =====================================================
        # ARTIST INTEREST
        # =====================================================

        if artist_name in user_artists:
            interest_score += 15

        # =====================================================
        # EXPLORATION
        # =====================================================

        exploration_score = 0

        if (
            days_old <= 7
            and total_seconds < 50000
            and unique_listeners < 30
        ):
            exploration_score = 8

        # =====================================================
        # DIVERSITY
        # =====================================================

        diversity_penalty = (
            -8
            if total_seconds > 3_000_000
            else 0
        )

        # =====================================================
        # RANDOMNESS
        # =====================================================

        noise = random.random() * 0.8

        # =====================================================
        # FINAL SCORE
        # =====================================================

        score = (
            freshness_score
            +
            engagement_score * 0.6
            +
            velocity_score * 0.7
            +
            popularity_score
            +
            interest_score
            +
            exploration_score
            +
            diversity_penalty
            +
            noise
        )

        scored.append(
            (
                score,
                song,
                artist_name,
            )
        )

    # =========================================================
    # SORT
    # =========================================================

    scored.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    # =========================================================
    # ARTIST DIVERSITY
    # =========================================================

    result = []

    artist_counter = {}

    for score, song, artist_name in scored:

        if not artist_name:
            continue

        if artist_counter.get(
            artist_name,
            0
        ) >= 2:
            continue

        result.append(song)

        artist_counter[artist_name] = (
            artist_counter.get(
                artist_name,
                0,
            )
            + 1
        )

        if len(result) >= limit:
            return result

    # =========================================================
    # FALLBACK 1
    # GLOBAL POPULAR
    # =========================================================

    if len(result) < limit:

        global_songs = (
            Songs.objects
            .filter(is_published=True)
            .order_by("-total_listen_time")[:100]
        )

        existing_ids = {
            song.id
            for song in result
        }

        for song in global_songs:

            if song.id in existing_ids:
                continue

            result.append(song)
            existing_ids.add(song.id)

            if len(result) >= limit:
                return result

    # =========================================================
    # FALLBACK 2
    # RANDOM
    # =========================================================

    if len(result) < limit:

        random_songs = list(
            Songs.objects
            .filter(is_published=True)
            .order_by("?")[:limit]
        )

        existing_ids = {
            song.id
            for song in result
        }

        for song in random_songs:

            if song.id in existing_ids:
                continue

            result.append(song)
            existing_ids.add(song.id)

            if len(result) >= limit:
                break

    return result