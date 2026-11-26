from datetime import timedelta
from django.utils import timezone
from math import log, exp

from music.models import Songs , SongListen , Album , UserSongInteraction
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from math import log, exp

from django.db import transaction
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, F, Sum
import random

@transaction.atomic
def register_skip(user, session_id):
    if not user.is_authenticated:
        raise ValidationError(
            "Authentication is required."
        )

    try:
        listen = (
            SongListen.objects
            .select_for_update()
            .select_related("song")
            .get(session_id=session_id)
        )

    except SongListen.DoesNotExist:
        raise ValidationError(
            "Listen session not found."
        )

    # =========================
    # Validate User
    # =========================

    if listen.user_id != user.id:
        raise ValidationError(
            "This session belongs to another user."
        )

    # =========================
    # Session already skipped
    # =========================

    if listen.skip_counted:
        return listen, False

    # =========================
    # Play must be counted
    # =========================

    if not listen.play_counted:
        return listen, False

    # =========================
    # Get Interaction
    # =========================

    interaction = (
        UserSongInteraction.objects
        .select_for_update()
        .filter(
            user=user,
            song=listen.song,
        )
        .first()
    )

    if interaction is None:
        raise ValidationError(
            "User-song interaction not found."
        )

    # =========================
    # Count Skip
    # =========================

    listen.skip_counted = True

    listen.save(
        update_fields=[
            "skip_counted",
        ]
    )

    interaction.skip_count += 1

    # =========================
    # Recalculate Skip Rate
    # =========================

    if interaction.play_count > 0:
        interaction.skip_rate = (
            interaction.skip_count
            / interaction.play_count
        )

    # =========================
    # Update Engagement
    # =========================

    interaction.engagement_score = (
        interaction.avg_listen_time * 0.4
        + interaction.completion_rate * 30
        + interaction.play_count * 2
        + interaction.replay_count * 3
        + (5 if interaction.liked else 0)
        + (5 if interaction.favorited else 0)
        - interaction.skip_rate * 10
    )

    interaction.last_session_id = (
        listen.session_id
    )

    interaction.last_interaction_at = (
        timezone.now()
    )

    interaction.save()

    return listen, True

def get_fresh_tracks(user, limit=20):

    now = timezone.now()
    min_date = now - timedelta(days=30)

    songs = (
        Songs.objects.filter(
            release_date__gte=min_date,
            is_published=True
        )
        .select_related("genre")
        .prefetch_related(
            "trackartist_set",
            "trackartist_set__artist"
        )
    )

    user_genres = set()
    user_artists = set()

    if user and user.is_authenticated:

        if hasattr(user, "favorite_genres"):
            user_genres = set(
                user.favorite_genres.values_list("id", flat=True)
            )

        if hasattr(user, "favorite_artists"):
            user_artists = set(
                user.favorite_artists.values_list("artistname", flat=True)
            )

    scored = []

    for song in songs:

        days_old = (now - song.release_date).days

        total_seconds = song.total_listen_time or 0
        unique_listeners = song.unique_listeners or 0
        plays_last_day = song.plays_last_24h or 0

        freshness_score = exp(-days_old / 5) * 45

        engagement = log(total_seconds + 1) + log(unique_listeners + 1)
        engagement_score = min(engagement * 3.5, 20)

        velocity_score = min(log(plays_last_day + 1) * 6, 18)

        popularity_score = min(log(total_seconds + 1) * 1.5, 12)

        interest_score = 0

        if song.genre_id in user_genres:
            interest_score += 10

        main_artist = None
        for rel in song.trackartist_set.all():
            if rel.role == "main":
                main_artist = rel.artist
                break

        if not main_artist:
            rels = list(song.trackartist_set.all())
            if rels:
                main_artist = rels[0].artist

        artist_name = main_artist.artistname if main_artist else None

        if artist_name in user_artists:
            interest_score += 15

        exploration_score = 0
        if days_old <= 7 and total_seconds < 50000 and unique_listeners < 30:
            exploration_score = 8

        diversity_penalty = -8 if total_seconds > 3_000_000 else 0

        noise = random.random() * 0.8

        score = (
            freshness_score +
            engagement_score * 0.6 +
            velocity_score * 0.7 +
            popularity_score +
            interest_score +
            exploration_score +
            diversity_penalty +
            noise
        )

        scored.append((score, song, artist_name))

    scored.sort(key=lambda x: x[0], reverse=True)

    result = []
    artist_counter = {}

    for score, song, artist_name in scored:

        if not artist_name:
            continue

        if artist_counter.get(artist_name, 0) >= 2:
            continue

        result.append(song)
        artist_counter[artist_name] = artist_counter.get(artist_name, 0) + 1

        if len(result) >= limit:
            return result

    # -------- Fallback 1: Global popular --------

    if len(result) < limit:

        global_songs = (
            Songs.objects.filter(is_published=True)
            .order_by("-total_listen_time")[:100]
        )

        for song in global_songs:

            if song in result:
                continue

            result.append(song)

            if len(result) >= limit:
                return result

    # -------- Fallback 2: Random --------

    if len(result) < limit:

        random_songs = list(
            Songs.objects.filter(is_published=True).order_by("?")[:limit]
        )

        for song in random_songs:

            if song in result:
                continue

            result.append(song)

            if len(result) >= limit:
                break

    return result





#GET TRENDING TRACK









def get_trending_tracks(limit=20, cache_ttl=120):

    cache_key = f"trending_{limit}"
    cached = cache.get(cache_key)

    if cached:
        return cached

    now = timezone.now()

    songs = (
        Songs.objects.filter(is_published=True)
        .prefetch_related(
            "trackartist_set",
            "trackartist_set__artist",
            "liked_by"
        )
    )

    scored = []

    for song in songs:

        total_plays = song.play_count or 0
        total_seconds = song.total_listen_time or 0
        unique_users = song.unique_listeners or 0
        plays_24 = song.plays_last_24h or 0

        if total_plays < 10:
            continue

        release_date = song.release_date
        days_old = (now - release_date).days if release_date else 0

        if days_old < 2:
            continue

        velocity_score = log(plays_24 + 1) * 12

        growth = plays_24 / (total_plays + 10)
        growth_score = min(growth * 80, 40)

        engagement_score = (
            log(total_seconds + 1) * 2 +
            log(unique_users + 1) * 4
        )

        viral_score = 0
        if total_plays > 20:
            spike = plays_24 / total_plays
            if spike > 0.35:
                viral_score = 25
            elif spike > 0.2:
                viral_score = 15

        likes = song.liked_by.count()
        like_score = min(log(likes + 1) * 6, 20)

        freshness_score = exp(-days_old / 20) * 6

        manipulation_penalty = 0
        if unique_users > 0:
            ppu = total_plays / unique_users
            if ppu > 25:
                manipulation_penalty = 20

        main_artist = None
        for rel in song.trackartist_set.all():
            if rel.role == "main":
                main_artist = rel.artist
                break

        if not main_artist:
            rels = list(song.trackartist_set.all())
            if rels:
                main_artist = rels[0].artist

        if not main_artist:
            continue

        artist_name = main_artist.artistname

        score = (
            velocity_score +
            growth_score +
            engagement_score +
            viral_score +
            like_score +
            freshness_score -
            manipulation_penalty
        )

        scored.append((score, song, artist_name))

    scored.sort(key=lambda x: x[0], reverse=True)

    result = []
    counter = {}

    for score, song, artist_name in scored:

        if counter.get(artist_name, 0) >= 2:
            continue

        result.append(song)
        counter[artist_name] = counter.get(artist_name, 0) + 1

        if len(result) >= limit:
            cache.set(cache_key, result, cache_ttl)
            return result

    # ---------- Fallback 1: Global Popular ----------

    if len(result) < limit:

        global_popular = (
            Songs.objects.filter(is_published=True)
            .order_by("-total_listen_time")[:100]
        )

        for song in global_popular:

            if song in result:
                continue

            result.append(song)

            if len(result) >= limit:
                cache.set(cache_key, result, cache_ttl)
                return result

    # ---------- Fallback 2: Fresh ----------

    if len(result) < limit:

        fresh = (
            Songs.objects.filter(is_published=True)
            .order_by("-release_date")[:100]
        )

        for song in fresh:

            if song in result:
                continue

            result.append(song)

            if len(result) >= limit:
                cache.set(cache_key, result, cache_ttl)
                return result

    # ---------- Fallback 3: Random ----------

    if len(result) < limit:

        random_songs = Songs.objects.filter(is_published=True).order_by("?")[:limit]

        for song in random_songs:

            if song in result:
                continue

            result.append(song)

            if len(result) >= limit:
                break

    cache.set(cache_key, result, cache_ttl)

    return result



# GETPOPULAR TRACK






def get_popular_albums(user=None, limit=20):

    albums = (
        Album.objects.filter(is_published=True)
        .prefetch_related(
            "tracks",
            "tracks__trackartist_set",
            "tracks__trackartist_set__artist",
        )
        .select_related("artist")
    )

    scored = []

    for album in albums:

        tracks = album.tracks.all()

        if not tracks.exists():
            continue

        # ---------------------------------------------------
        # Aggregate album-level stats (Spotify style)
        # ---------------------------------------------------

        total_seconds = tracks.aggregate(s=Sum("total_listen_time"))["s"] or 0
        total_plays = tracks.aggregate(p=Sum("play_count"))["p"] or 0
        total_unique = tracks.aggregate(u=Sum("unique_listeners"))["u"] or 0

        track_count = tracks.count()

        # ---------------------------------------------------
        # 1) LISTEN TIME
        # ---------------------------------------------------
        listen_score = log(total_seconds + 1) * 4

        # ---------------------------------------------------
        # 2) PLAY COUNT
        # ---------------------------------------------------
        play_score = log(total_plays + 1) * 3

        # ---------------------------------------------------
        # 3) UNIQUE LISTENERS
        # ---------------------------------------------------
        listener_score = log(total_unique + 1) * 5

        # ---------------------------------------------------
        # 4) HIT TRACK BOOST
        # (وقتی آلبوم چند ترک خیلی موفق دارد)
        # ---------------------------------------------------

        hit_tracks = tracks.filter(play_count__gte=500).count()
        hit_boost = hit_tracks * 4  # هر ترک موفق ۴ امتیاز

        # ---------------------------------------------------
        # 5) CONSISTENCY BONUS
        # (وقتی همه ترک‌ها شنیده می‌شوند)
        # ---------------------------------------------------

        consistency = 0
        if track_count >= 5:
            highly_played = tracks.filter(play_count__gte=100).count()
            if highly_played >= track_count * 0.7:
                consistency = 10

        # ---------------------------------------------------
        # ARTIST NAME
        # ---------------------------------------------------

        artist_name = album.artist.artistname if album.artist else None

        # ---------------------------------------------------
        # FINAL SCORE
        # ---------------------------------------------------

        score = (
            listen_score +
            play_score +
            listener_score +
            hit_boost +
            consistency
        )

        scored.append((score, album, artist_name))

    # sort albums by score
    scored.sort(key=lambda x: x[0], reverse=True)

    # ---------------------------------------------------
    # LIMIT 2 ALBUMS PER ARTIST (Spotify style)
    # ---------------------------------------------------

    result = []
    artist_counter = {}

    for score, album, artist_name in scored:

        if not artist_name:
            continue

        count = artist_counter.get(artist_name, 0)
        if count >= 2:
            continue

        result.append(album)

        artist_counter[artist_name] = count + 1
        if len(result) >= limit:
            break

    return result


# from django.utils import timezone
# from datetime import timedelta


from django.db import transaction
from django.core.exceptions import ValidationError

from music.models import SongListen


from django.db import transaction
from django.core.exceptions import ValidationError

from music.models import SongListen


@transaction.atomic
def register_listen(song, user, seconds, session_id):

    if seconds <= 0:
        return None, False

    # =========================
    # Get / Create Session
    # =========================

    user_id = user.pk if user.is_authenticated else None
    listen, _ = SongListen.objects.select_for_update().get_or_create(
        session_id=session_id,
        defaults={"song": song, "user_id": user_id},
    )

    # =========================
    # Validate Song
    # =========================

    if listen.song_id != song.id:
        raise ValidationError(
            "This session belongs to another song."
        )

    # =========================
    # Validate User
    # =========================

    if listen.user_id != user_id:
        raise ValidationError(
            "This session belongs to another user."
        )

    # =========================
    # Calculate Delta
    # =========================

    old_seconds = listen.seconds_listened

    reported_seconds = min(seconds, song.duration) if song.duration else seconds
    new_seconds = max(old_seconds, reported_seconds)

    added_seconds = new_seconds - old_seconds

    if added_seconds <= 0:
        return listen, False

    # =========================
    # Update Session
    # =========================

    listen.seconds_listened = new_seconds

    # =========================
    # Play Count
    # =========================

    play_counted = False

    if (
        not listen.play_counted
        and old_seconds < 30 <= new_seconds
    ):
        listen.play_counted = True

        play_counted = True

    # =========================
    # Completion
    # =========================

    completed = False

    if (
        not listen.completion_counted
        and song.duration > 0
        and new_seconds >= song.duration * 0.9
    ):
        listen.completion_counted = True

        completed = True

    # =========================
    # Save Listen
    # =========================

    listen.save(
        update_fields=[
            "seconds_listened",
            "play_counted",
            "completion_counted",
        ]
    )

    # =========================
    # Song Statistics
    # =========================

    Songs.objects.filter(pk=song.pk).update(
        total_listen_time=F("total_listen_time") + added_seconds,
        play_count=F("play_count") + int(play_counted),
    )

    # =========================
    # User Interaction
    # =========================

    if user.is_authenticated:

        if listen.play_counted:

            interaction, created = (
                UserSongInteraction.objects
                .select_for_update()
                .get_or_create(
                    user=user,
                    song=song,
                )
            )

            # =========================
            # Listen Time Delta
            # =========================

            interaction_delta = (
                new_seconds
                - listen.interaction_seconds_recorded
            )

            if interaction_delta > 0:

                interaction.total_listen_time += (
                    interaction_delta
                )

            # =========================
            # Play Count
            # =========================

            if play_counted:
                interaction.play_count += 1

            # =========================
            # Completion
            # =========================

            if completed:
                interaction.completed_count += 1

            # =========================
            # Metrics
            # =========================

            if interaction.play_count > 0:

                interaction.avg_listen_time = (
                    interaction.total_listen_time
                    / interaction.play_count
                )

                interaction.completion_rate = (
                    interaction.completed_count
                    / interaction.play_count
                )

                interaction.skip_rate = (
                    interaction.skip_count
                    / interaction.play_count
                )

            # =========================
            # Session Metadata
            # =========================

            interaction.last_session_id = (
                listen.session_id
            )

            interaction.last_interaction_at = (
                timezone.now()
            )

            # =========================
            # Engagement Score
            # =========================

            interaction.engagement_score = (
                interaction.avg_listen_time * 0.4
                + interaction.completion_rate * 30
                + interaction.play_count * 2
                + interaction.replay_count * 3
                + (5 if interaction.liked else 0)
                + (5 if interaction.favorited else 0)
                - interaction.skip_rate * 10
            )

            interaction.save()

            # =========================
            # Mark Aggregated Seconds
            # =========================

            listen.interaction_seconds_recorded = (
                new_seconds
            )

            listen.save(
                update_fields=[
                    "interaction_seconds_recorded",
                ]
            )

    return listen, play_counted

# def register_listen(song, user, seconds):
#     now = timezone.now()
#     cutoff = now - timedelta(seconds=60)

#     # 1) block spam plays
#     recent_play = SongListen.objects.filter(
#         user=user, 
#         song=song,
#         listened_at__gte=cutoff
#     ).exists()

#     if recent_play:
#         return False

#     # 2) register clean listen
#     SongListen.objects.create(
#         user=user,
#         song=song,
#         seconds_listened=seconds,
#     )

#     song.play_count += 1
#     song.total_listen_time += seconds
#     song.save(update_fields=['play_count', 'total_listen_time'])

#     return True


# def get_similar_users(user, limit=20):
#     user_songs = SongListen.objects.filter(user=user).values_list('song_id', flat=True)

#     return (
#         SongListen.objects
#         .exclude(user=user)
#         .filter(song_id__in=user_songs)
#         .values('user')
#         .annotate(shared=Count('song'))
#         .order_by('-shared')[:limit]
#     )
