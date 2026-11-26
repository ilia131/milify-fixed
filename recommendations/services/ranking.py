from collections import namedtuple
import numpy as np
from music.models import Songs
from .candidate_generation import (
    candidates_from_genre,
    candidates_from_artists,
    candidates_from_user_history,
    candidates_from_trending,
)
from .similarity import song_to_playlist_similarity, cosine_sim
from .feature_extraction import song_embedding, popularity_vector, recency_vector
from .user_profile import user_embedding

RankedSong = namedtuple("RankedSong", ["song", "score", "meta"])


def rank_songs_for_playlist(user, current_songs, limit=20):
    current_songs = list(current_songs)

    cands = (
        list(candidates_from_genre(current_songs))
        + list(candidates_from_artists(current_songs))
        + list(candidates_from_user_history(user))
        + list(candidates_from_trending())
    )

    # حذف تکراری‌ها و آهنگ‌های فعلی
    uniq = {s.id: s for s in cands}.values()
    current_ids = {s.id for s in current_songs}
    candidates = [s for s in uniq if s.id not in current_ids]

    if not candidates:
        return []

    user_emb = user_embedding(user)
    playlist_ref = current_songs or candidates[:10]

    ranked = []

    for song in candidates:
        emb = song_embedding(song)
        sim_pl = song_to_playlist_similarity(song, playlist_ref)
        sim_user = cosine_sim(emb, user_emb)
        pop = float(popularity_vector(song)[0])
        rec = float(recency_vector(song)[0])

        score = 0.4 * sim_pl + 0.3 * sim_user + 0.2 * pop + 0.1 * rec
        meta = dict(sim_playlist=sim_pl, sim_user=sim_user, pop=pop, rec=rec)
        ranked.append(RankedSong(song=song, score=score, meta=meta))

    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked[:limit]
