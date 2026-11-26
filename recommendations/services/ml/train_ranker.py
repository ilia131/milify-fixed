import xgboost as xgb
import joblib
import numpy as np

from music.models import Songs
from accounts.models import UserListener
from .features import build_features

MODEL_PATH = "ranker_model.joblib"


def train_ranker():

    X = []
    y = []

    users = UserListener.objects.all()[:200]

    for user in users:

        songs = Songs.objects.order_by("?")[:200]

        for song in songs:

            features = build_features(user, song)

            label = 0

            if song.total_listen_time and song.total_listen_time > 1000:
                label = 1

            X.append(features)
            y.append(label)

    X = np.array(X)
    y = np.array(y)

    model = xgb.XGBRanker(
        objective="rank:pairwise",
        learning_rate=0.1,
        max_depth=6,
        n_estimators=100
    )

    group = [len(X)]

    model.fit(X, y, group=group)

    joblib.dump(model, MODEL_PATH)

    print("✅ Ranker trained")
