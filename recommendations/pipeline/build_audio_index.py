import os
import faiss
import numpy as np
from django.conf import settings
from music.models import Songs

INDEX_PATH = os.path.join(settings.BASE_DIR, "models_ml", "audio.index")


def build_audio_index():

    songs = Songs.objects.all()

    vectors = []

    for s in songs:
        vectors.append([
            s.energy,
            s.danceability,
            s.tempo,
            s.valence,
            s.acousticness,   
            s.loudness or 0.0,
        ])

    if not vectors:
        print("No songs found for FAISS index")
        return None

    vectors = np.array(vectors).astype("float32")

    d = vectors.shape[1]

    index = faiss.IndexFlatL2(d)
    index.add(vectors)

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    print("Audio FAISS index built")

    return index
