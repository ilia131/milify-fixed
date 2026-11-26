import joblib
import numpy as np
from music.models import Songs
from django.conf import settings
import os


MODEL_PATH = os.path.join(settings.BASE_DIR, "recommendations", "ml_model.joblib")


def recommend_for_user(user_id, limit=20):
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError("مدل آموزش داده نشده است!")

    obj = joblib.load(MODEL_PATH)
    model = obj["model"]
    mapping = obj["mapping"]

    if user_id not in mapping["user_to_index"]:
        # کاربر جدید → fallback به trending
        return Songs.objects.filter(is_published=True).order_by("-play_count")[:limit]

    user_index = mapping["user_to_index"][user_id]

    # پیش‌بینی برای کاربر
    recs = model.recommend(
        userid=user_index,
        user_items=None,
        N=limit
    )

    song_indices = [int(i) for i, score in recs]
    song_ids = [list(mapping["song_to_index"].keys())[i] for i in song_indices]

    return list(Songs.objects.filter(id__in=song_ids))
