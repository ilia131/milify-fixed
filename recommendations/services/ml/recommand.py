from music.models import Songs
from .loader import load_model
from .fallback import fallback_mix
from .background import train_async
import numpy as np


def recommend_for_user(user_id, limit=50):
    model = load_model()
    if model is None:
        return fallback_mix(limit)

    user_id = str(user_id).lower()

    if user_id not in model["user_uids"]:
        return fallback_mix(limit)

    vec = model["user_embed"][user_id].astype("float32")

    distances, idxs = model["faiss"].search(np.array([vec]), limit*3)

    candidates = [model["song_uids"][idx] for idx in idxs[0]]

    # Remove duplicates
    unique = []
    seen = set()
    for uid in candidates:
        if uid not in seen:
            seen.add(uid)
            unique.append(uid)
            if len(unique) >= limit:
                break

    queryset = list(
        Songs.objects.filter(song_id__in=unique)
        .prefetch_related("artists")
    )

    id_to_song = {str(s.song_id).lower(): s for s in queryset}

    return [id_to_song[i] for i in unique if i in id_to_song]



def recommend_from_playlist(song_uids, limit=50):
    model = load_model()
    if model is None:
        return fallback_mix(limit)

    # Normalize case
    song_uids = [str(x).lower() for x in song_uids]

    # Filter only valid IDs
    input_uids = [
        uid for uid in song_uids if uid in model["song_uids"]
    ]

    if not input_uids:
        return fallback_mix(limit)

    # Aggregate embeddings for playlist
    vectors = [model["song_embed"][uid] for uid in input_uids]
    playlist_vec = np.mean(vectors, axis=0).astype("float32")

    # FAISS search
    distances, indices = model["faiss"].search(np.array([playlist_vec]), limit*3)

    # Map back to song UUIDs
    candidates = []
    for idx in indices[0]:
        uid = model["song_uids"][idx]
        if uid not in input_uids:
            candidates.append(uid)

    # Remove duplicates
    seen = set()
    final_ids = []
    for uid in candidates:
        if uid not in seen:
            seen.add(uid)
            final_ids.append(uid)
            if len(final_ids) >= limit:
                break

    queryset = list(
        Songs.objects.filter(song_id__in=final_ids)
        .prefetch_related("artists")
    )
    id_to_song = {str(s.song_id).lower(): s for s in queryset}

    return [id_to_song[i] for i in final_ids if i in id_to_song]






def recommend_suggest(seed_song_ids=None, seed_artist_ids=None, seed_genres=None, limit=30):
    import numpy as np

    model = load_model()

    # اگر مدل نبود
    if model is None:
        return list(Songs.objects.filter(genre__in=seed_genres or [])[:limit])

    song_embed = model["song_embed"]
    song_uids = [str(u).lower() for u in model["song_uids"]]
    index = model["faiss"]

    seed_vectors = []

    # -------- seed songs --------
    if seed_song_ids:
        for uid in seed_song_ids:

            uid_str = str(uid).lower()

            if uid_str in song_uids:
                idx = song_uids.index(uid_str)
                seed_vectors.append(song_embed[idx])

            else:
                try:
                    s = Songs.objects.get(unique_id=uid)
                    if s.genre:
                        seed_genres = (seed_genres or []) + [s.genre]
                except Songs.DoesNotExist:
                    pass

    # -------- seed artists --------
    if seed_artist_ids:

        songs = Songs.objects.filter(artist_id__in=seed_artist_ids)[:20]

        for s in songs:

            uid_str = str(s.unique_id).lower()

            if uid_str in song_uids:
                idx = song_uids.index(uid_str)
                seed_vectors.append(song_embed[idx])

    # -------- seed genres --------
    if seed_genres:

        songs = Songs.objects.filter(
            genre__in=seed_genres
        ).order_by("-play_count")[:20]

        for s in songs:

            uid_str = str(s.unique_id).lower()

            if uid_str in song_uids:
                idx = song_uids.index(uid_str)
                seed_vectors.append(song_embed[idx])

    # -------- fallback --------
    if not seed_vectors:

        if seed_genres:
            return list(
                Songs.objects.filter(
                    genre__in=seed_genres
                ).order_by("-play_count")[:limit]
            )

        return list(
            Songs.objects.order_by("-play_count")[:limit]
        )

    # -------- FAISS search --------
    seed_vec = np.mean(seed_vectors, axis=0).astype("float32")

    k = limit * 10

    D, I = index.search(seed_vec.reshape(1, -1), k)

    suggested_uuids = []

    for i in I[0]:

        if i < len(song_uids):
            suggested_uuids.append(song_uids[i])

    # -------- filtering --------
    bad_seeds = set([str(u).lower() for u in (seed_song_ids or [])])

    seen_artists = {}
    final_songs = []
    seen_songs = set()

    for uid in suggested_uuids:

        if uid in bad_seeds:
            continue

        if uid in seen_songs:
            continue

        try:

            s = Songs.objects.select_related("artist").get(unique_id=uid)

            artist_id = s.artist_id

            if artist_id not in seen_artists:
                seen_artists[artist_id] = 0

            if seen_artists[artist_id] >= 2:
                continue

            seen_artists[artist_id] += 1
            seen_songs.add(uid)

            final_songs.append(s)

        except Songs.DoesNotExist:
            continue

        if len(final_songs) >= limit:
            break

    # اگر هنوز خالی بود
    if not final_songs:
        return list(
            Songs.objects.order_by("-play_count")[:limit]
        )

    return final_songs
