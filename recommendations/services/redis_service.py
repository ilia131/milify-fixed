from django_redis import get_redis_connection


def get_redis():
    return get_redis_connection("default")


# =========================================================
# SONG STATS
# =========================================================

def get_song_plays_24h(song_id):
    redis = get_redis()

    key = f"song:{song_id}:plays:24h"

    return redis.zcard(key)


def get_song_unique_listeners(song_id):
    redis = get_redis()

    key = f"song:{song_id}:unique:listeners"

    return redis.scard(key)


# =========================================================
# ARTIST STATS
# =========================================================

def get_artist_monthly_listeners(artist_id):
    redis = get_redis()

    key = f"artist:{artist_id}:monthly:listeners"

    return redis.zcard(key)


# =========================================================
# FOR YOU CACHE
# =========================================================

def get_user_recommendations(user_id):
    redis = get_redis()

    key = f"recommendations:user:{user_id}"

    return redis.get(key)


def set_user_recommendations(user_id, song_ids, timeout=300):
    redis = get_redis()

    key = f"recommendations:user:{user_id}"

    redis.set(
        key,
        ",".join(str(song_id) for song_id in song_ids),
        ex=timeout,
    )


def delete_user_recommendations(user_id):
    redis = get_redis()

    key = f"recommendations:user:{user_id}"

    redis.delete(key)