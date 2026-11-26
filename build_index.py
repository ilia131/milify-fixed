import os
import django
import numpy as np
import faiss

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from recommendations.models import Songs

vectors = []

for song in Songs.objects.all():
    vec = np.array([
        song.tempo,
        song.energy,
        song.danceability,
        song.loudness,
        song.valence,
        song.acousticness,
    ], dtype="float32")
    
    vectors.append(vec)

vectors = np.array(vectors).astype("float32")

dim = vectors.shape[1]

index = faiss.IndexHNSWFlat(dim, 32)
index.add(vectors)

faiss.write_index(index, "songs.faiss")

print("✅ FAISS index created")
print("dimension:", dim)
print("songs:", len(vectors))
