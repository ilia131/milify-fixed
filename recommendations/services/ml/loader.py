import joblib
import faiss
import os

def load_model():
    model_path = "models/recommender_data.joblib"
    faiss_path = "models/song_index.faiss"

    if not os.path.exists(model_path) or not os.path.exists(faiss_path):
        return None

    try:
        # لود کردن دیتا (شامل لیست‌های uids و embeddings)
        data = joblib.load(model_path)
        # لود کردن ایندکس فیس
        index = faiss.read_index(faiss_path)
        
        # ترکیب در یک دیکشنری واحد
        return {
            "faiss": index,
            "user_uids": data["user_uids"],
            "song_uids": data["song_uids"],
            "user_embed": data["user_embed"],
            "song_embed": data["song_embed"],
        }
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
