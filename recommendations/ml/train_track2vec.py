from gensim.models import Word2Vec
from music.models import PlaylistTrack


def train():

    playlists = {}

    for p in PlaylistTrack.objects.all():
        playlists.setdefault(p.playlist_id, []).append(str(p.song_id))

    sequences = list(playlists.values())

    if not sequences:
        print("❌ No playlist data found. Cannot train Track2Vec.")
        return

    print(f"Training on {len(sequences)} playlists")

    model = Word2Vec(
        sentences=sequences,
        vector_size=64,
        window=5,
        min_count=1,
        workers=4,
        epochs=20
    )

    model.save("track2vec.model")

    print("✅ Track2Vec trained successfully")
