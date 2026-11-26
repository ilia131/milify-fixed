import faiss
import numpy as np
from music.models import Songs
from .feature_builder import FeatureBuilder


def build():

    songs = list(Songs.objects.filter(is_published=True))

    if not songs:
        print("No songs found")
        return

    vectors = []
    ids = []

    for s in songs:
        vectors.append(FeatureBuilder.build(s))
        ids.append(s.id)

    vectors = np.array(vectors).astype("float32")

    dim = vectors.shape[1]
    n = len(vectors)

    print(f"Building index for {n} songs (dim={dim})")

    # ✅ Adaptive selection
    if n < 100:
        print("Using IndexFlatL2 (small dataset)")
        index = faiss.IndexFlatL2(dim)

    elif n < 5000:
        print("Using HNSW index")
        index = faiss.IndexHNSWFlat(dim, 32)

    elif n < 200000:
        print("Using IVF index")
        nlist = min(100, n // 10)
        quantizer = faiss.IndexFlatL2(dim)
        index = faiss.IndexIVFFlat(quantizer, dim, nlist)
        index.train(vectors)

    else:
        print("Using IVF-PQ index (large scale)")
        nlist = min(1024, n // 100)
        M = dim  # ✅ safe choice
        quantizer = faiss.IndexFlatL2(dim)
        index = faiss.IndexIVFPQ(
            quantizer,
            dim,
            nlist,
            M,
            8
        )
        index.train(vectors)

    index.add(vectors)

    faiss.write_index(index, "songs_ann.index")
    np.save("songs_ids.npy", np.array(ids))

    print("✅ Index built successfully")
