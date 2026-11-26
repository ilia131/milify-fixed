import os
from gensim.models import Word2Vec
from django.conf import settings
from music.models import PlaylistTrack

MODEL_PATH = os.path.join(settings.BASE_DIR, "models_ml", "track2vec.model")


def train_track2vec():

    playlists = PlaylistTrack.objects.values_list(
        "playlist_id", flat=True
    ).distinct()

    sequences = []

    for pid in playlists:
        tracks = PlaylistTrack.objects.filter(
            playlist_id=pid
        ).order_by("position")

        sequences.append([str(t.song_id) for t in tracks])

    if not sequences:
        print("No playlist data found for Track2Vec training")
        return None

    model = Word2Vec(
        sentences=sequences,
        vector_size=64,
        window=5,
        min_count=1,
        workers=4
    )

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save(MODEL_PATH)

    print("Track2Vec model trained")

    return model
