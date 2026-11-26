from music.models import Songs, UserSongInteraction

from music.ml.feature_engineering import (
    calculate_song_age_days,
    get_user_song_features,
    get_user_taste_profile,
)


def build_song_features(
    song: Songs,
    interaction: UserSongInteraction | None = None,
    user_profile: dict | None = None,
) -> dict:

    # =========================================================
    # USER PROFILE
    # =========================================================

    if user_profile is None:

        user_profile = get_user_taste_profile(
            user_id=interaction.user_id
            if interaction
            else 0
        )

    # =========================================================
    # INTERACTION
    # =========================================================

    interaction_data = get_user_song_features(
        interaction
    )

    # =========================================================
    # SONG FEATURES
    # =========================================================

    return {
        "song_id": song.id,

        "popularity": float(
            song.popularity or 0
        ),

        "tempo": float(
            song.tempo or 0
        ),

        "energy": float(
            song.energy or 0
        ),

        "danceability": float(
            song.danceability or 0
        ),

        "valence": float(
            song.valence or 0
        ),

        "acousticness": float(
            song.acousticness or 0
        ),

        "unique_listeners": int(
            song.unique_listeners or 0
        ),

        "play_count": int(
            song.play_count or 0
        ),

        "total_listen_time": int(
            song.total_listen_time or 0
        ),

        "plays_last_24h": int(
            song.plays_last_24h or 0
        ),

        "song_age_days": calculate_song_age_days(
            song
        ),

        # =====================================================
        # INTERACTION
        # =====================================================

        "interaction": {
            "play_count": interaction_data[
                "interaction_play_count"
            ],

            "total_listen_time": interaction_data[
                "interaction_total_listen_time"
            ],

            "avg_listen_time": interaction_data[
                "interaction_avg_listen_time"
            ],

            "skip_count": interaction_data[
                "interaction_skip_count"
            ],

            "skip_rate": interaction_data[
                "interaction_skip_rate"
            ],

            "completed_count": interaction_data[
                "interaction_completed_count"
            ],

            "completion_rate": interaction_data[
                "interaction_completion_rate"
            ],

            "engagement_score": interaction_data[
                "interaction_engagement_score"
            ],
        },

        # =====================================================
        # USER TASTE PROFILE
        # =====================================================

        "user_profile": {
            "avg_tempo": user_profile[
                "profile_avg_tempo"
            ],

            "avg_energy": user_profile[
                "profile_avg_energy"
            ],

            "avg_danceability": user_profile[
                "profile_avg_danceability"
            ],

            "avg_valence": user_profile[
                "profile_avg_valence"
            ],

            "avg_acousticness": user_profile[
                "profile_avg_acousticness"
            ],

            "avg_popularity": user_profile[
                "profile_avg_popularity"
            ],

            "total_play_count": user_profile[
                "profile_total_play_count"
            ],

            "total_listen_time": user_profile[
                "profile_total_listen_time"
            ],

            "avg_completion_rate": user_profile[
                "profile_avg_completion_rate"
            ],

            "avg_skip_rate": user_profile[
                "profile_avg_skip_rate"
            ],
        },
    }