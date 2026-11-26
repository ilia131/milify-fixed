import numpy as np
from django.utils import timezone
from music.models import Songs


def audio_features_vector(song: Songs):

    af = song.audio_features or {}

    return np.array([
        float(af.get("danceability", 0)),
        float(af.get("energy", 0)),
        float(af.get("valence", 0)),
        float(af.get("acousticness", 0)),
        float(af.get("instrumentalness", 0)),
        float(af.get("liveness", 0)),
        float(af.get("speechiness", 0)),
        float(af.get("tempo", 0)) / 250
    ])


def genre_vector(song: Songs):

    vec = np.zeros(32)

    if song.genre_id:
        idx = song.genre_id % 32
        vec[idx] = 1

    return vec


def popularity_vector(song: Songs):

    pc = song.play_count or 0
    score = np.log1p(pc) / 10

    return np.array([score])


def recency_vector(song: Songs):

    if not song.release_date:
        return np.array([0])

    days = (timezone.now() - song.release_date).days

    score = np.exp(-days / 365)

    return np.array([score])


def song_embedding(song: Songs):

    g = genre_vector(song)
    af = audio_features_vector(song)
    pop = popularity_vector(song)
    rec = recency_vector(song)

    return np.concatenate([g, af, pop, rec])
