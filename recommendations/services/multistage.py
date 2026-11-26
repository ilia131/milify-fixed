import numpy as np
from music.models import Songs

from recommendations.services.ml import recommend_for_user
from recommendations.services.ranking import RankedSong
from recommendations.services.user_profile import user_embedding
from recommendations.services.feature_extraction import (
    song_embedding,
    popularity_vector,
    recency_vector,
)
from recommendations.services.similarity import (
    cosine_sim,
    song_to_playlist_similarity
)
from recommendations.services.candidate_generation import (
    candidates_from_genre,
    candidates_from_artists,
    candidates_from_trending,
)


def multistage_recommender(user, playlist_songs, limit=20):
    playlist_songs = list(playlist_songs)

    # -----------------------
    # Stage 1: Candidate Generation
    # -----------------------

    # 1) ML model
    ml_candidates = recommend_for_user(user.id, limit=300)

    # 2) Content / Genre
    genre_candidates = list(candidates_from_genre(playlist_songs, limit=300))

    # 3) Content / Artist
    artist_candidates = list(candidates_from_artists(playlist_songs, limit=300))

    # 4) Trending
    trending_candidates = list(candidates_from_trending(limit=200))

    # ادغام اولیه
    all_candidates = (
        list(ml_candidates)
        + list(genre_candidates)
        + list(artist_candidates)
        + list(trending_candidates)
    )

    # حذف آهنگ‌های موجود در پلی‌لیست
    playlist_ids = {s.id for s in playlist_songs}
    all_candidates = [
        s for s in all_candidates if s.id not in playlist_ids
    ]

    # حذف تکراری‌ها
    uniq = {s.id: s for s in all_candidates}
    candidates = list(uniq.values())

    if not candidates:
        return []

    # -----------------------
    # Stage 2: ML scoring + hybrid re-ranking
    # -----------------------
    user_emb = user_embedding(user)
    playlist_ref = playlist_songs or candidates[:10]

    ranked = []

    for song in candidates:
        emb = song_embedding(song)

        # Similarities
        sim_playlist = song_to_playlist_similarity(song, playlist_ref)
        sim_user = cosine_sim(emb, user_emb)

        # Simple ML score: اگر آهنگ در خروجی ML کانديد بود، وزن بده
        ml_boost = 1.0 if song in ml_candidates else 0.0

        # Popularity
        pop = float(popularity_vector(song)[0])

        # Recency
        rec = float(recency_vector(song)[0])

        # ترکیب نهایی
        score = (
            0.40 * sim_playlist +
            0.25 * sim_user +
            0.20 * ml_boost +
            0.10 * pop +
            0.05 * rec
        )

        ranked.append(
            RankedSong(song=song, score=score, meta={
                "sim_playlist": sim_playlist,
                "sim_user": sim_user,
                "ml": ml_boost,
                "pop": pop,
                "rec": rec,
            })
        )

    ranked.sort(key=lambda x: x.score, reverse=True)

    # Diversity boost: جلوگیری از آهنگ‌های بیش‌ازحد شبیه
    final = []
    seen_artists = set()

    for r in ranked:
        # جلوگیری از زیادی شدن آهنگ‌های یک آرتیست
        song_artists = set(r.song.artist.values_list("id", flat=True))
        if seen_artists & song_artists:
            continue
        seen_artists |= song_artists
        final.append(r.song)
        if len(final) >= limit:
            break

    # اگر diversity حذف زیاد کرد، از ranked ادامه می‌دهیم
    if len(final) < limit:
        rest_needed = limit - len(final)
        remaining = [r.song for r in ranked if r.song not in final]
        final += remaining[:rest_needed]

    return final
