import pandas as pd
from music.models import SongListen, LikedSong


def build_interaction_dataframe():
    rows = []

    for x in SongListen.objects.select_related("song"):
        rows.append({
            "user_id": x.user_id,
            "song_uid": str(x.song.unique_id),
            "weight": min(x.seconds_listened / 30, 5)
        })

    for x in LikedSong.objects.select_related("song"):
        rows.append({
            "user_id": x.user_id,
            "song_uid": str(x.song.unique_id),
            "weight": 4
        })

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # جمع‌زدن تکراری‌ها برای هر user-song و مرتب‌سازی قطعی برای SVD
    df = (
        df.groupby(["user_id", "song_uid"], as_index=False)
        .agg({"weight": "sum"})
        .sort_values(["user_id", "song_uid"])  # 🟢 مهم برای حفظ order ثابت
        .reset_index(drop=True)
    )

    # تبدیل به نوع categoric ولی با ترتیب مشخص
    df["user_cat"] = pd.Categorical(df["user_id"], ordered=True)
    df["song_cat"] = pd.Categorical(df["song_uid"], ordered=True)

    return df
