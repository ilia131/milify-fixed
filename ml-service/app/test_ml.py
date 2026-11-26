import requests

url = "http://127.0.0.1:8001/recommend"

payload = {
    "user": {
        "user_id": 1
    },
    "songs": [
        {
            "song_id": 3,
            "popularity": 50,
            "tempo": 120,
            "energy": 0.8,
            "danceability": 0.7,
            "valence": 0.6,
            "acousticness": 0.2,
            "unique_listeners": 100,
            "play_count": 200,
            "total_listen_time": 5000,
            "plays_last_24h": 30,
            "song_age_days": 10,
            "interaction": {
                "play_count": 5,
                "total_listen_time": 300,
                "avg_listen_time": 60,
                "skip_count": 0,
                "skip_rate": 0,
                "completed_count": 3,
                "completion_rate": 0.6,
                "engagement_score": 0.8
            }
        },
        {
            "song_id": 4,
            "popularity": 20,
            "tempo": 110,
            "energy": 0.4,
            "danceability": 0.5,
            "valence": 0.3,
            "acousticness": 0.5,
            "unique_listeners": 20,
            "play_count": 30,
            "total_listen_time": 500,
            "plays_last_24h": 5,
            "song_age_days": 20,
            "interaction": {
                "play_count": 0,
                "total_listen_time": 0,
                "avg_listen_time": 0,
                "skip_count": 0,
                "skip_rate": 0,
                "completed_count": 0,
                "completion_rate": 0,
                "engagement_score": 0
            }
        }
    ]
}

session = requests.Session()
session.trust_env = False

response = session.post(
    url,
    json=payload,
)
print("STATUS:", response.status_code)
print("RESPONSE:")
print(response.text)