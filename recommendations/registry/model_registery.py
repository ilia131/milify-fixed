import faiss
import os
import joblib

BASE_DIR = "models"


class ModelRegistry:
    _audio_index = None
    _track2vec = None

    @classmethod
    def audio_index(cls):
        if cls._audio_index is None:
            path = os.path.join(BASE_DIR, "audio.index")
            if not os.path.exists(path):
                raise RuntimeError("Audio index not found. Train first.")
            cls._audio_index = faiss.read_index(path)
        return cls._audio_index

    @classmethod
    def track2vec(cls):
        if cls._track2vec is None:
            path = os.path.join(BASE_DIR, "track2vec.model")
            if not os.path.exists(path):
                raise RuntimeError("Track2Vec model not found. Train first.")
            cls._track2vec = joblib.load(path)
        return cls._track2vec