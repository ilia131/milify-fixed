import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .feature_extraction import song_embedding


def cosine_sim(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    if vec_a is None or vec_b is None:
        return 0.0
    if np.linalg.norm(vec_a) == 0 or np.linalg.norm(vec_b) == 0:
        return 0.0
    return float(cosine_similarity(vec_a.reshape(1, -1), vec_b.reshape(1, -1))[0][0])


def song_to_playlist_similarity(song, playlist_songs):
    if not playlist_songs:
        return 0.0
    emb_song = song_embedding(song)
    embs_playlist = [song_embedding(s) for s in playlist_songs]
    sims = [cosine_sim(emb_song, e) for e in embs_playlist]
    return float(np.mean(sims))
