import joblib
import os
import numpy as np

from .features import build_features

MODEL_PATH = "ranker_model.joblib"

model = None


def load_model():
    global model

    if model is None and os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)

    return model


def rerank_songs(user, songs):

    model = load_model()

    if model is None:
        return songs

    features = []

    for s in songs:
        features.append(build_features(user, s))

    X = np.array(features)

    scores = model.predict(X)

    ranked = sorted(
        zip(scores, songs),
        key=lambda x: x[0],
        reverse=True
    )

    return [s for _, s in ranked]
