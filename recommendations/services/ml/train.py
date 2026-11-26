import os
import joblib
import numpy as np
import faiss
from django.conf import settings
from .data_setbuilder import build_interaction_dataframe

MODEL_PATH = os.path.join(settings.BASE_DIR, "recommendations/ml_model.joblib")


def train_ml_model():
    df = build_interaction_dataframe()

    if df.empty:
        return None

    user_ids = df["user_id"].astype("category")
    song_ids = df["song_uid"].astype("category")

    n_users = len(user_ids.cat.categories)
    n_songs = len(song_ids.cat.categories)

    matrix = np.zeros((n_users, n_songs), dtype="float32")

    for _, row in df.iterrows():
        ui = user_ids.cat.categories.get_loc(row["user_id"])
        si = song_ids.cat.categories.get_loc(row["song_uid"])
        matrix[ui, si] = row["weight"]

    U, S, Vt = np.linalg.svd(matrix, full_matrices=False)

    dim = min(64, Vt.shape[0])

    user_embed = (U[:, :dim] * S[:dim]).astype("float32")
    song_embed = Vt[:dim].T.astype("float32")

    index = faiss.IndexFlatIP(dim)
    index.add(song_embed)

    model = {
        "faiss": index,
        "user_embed": user_embed,
        "song_embed": song_embed,
        "user_uids": list(user_ids.cat.categories),
        "song_uids": list(song_ids.cat.categories)
        
    }

    joblib.dump(model, MODEL_PATH)

    return model
