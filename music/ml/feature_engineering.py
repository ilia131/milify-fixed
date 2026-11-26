from datetime import datetime, time

from django.utils import timezone

from music.models import Songs, UserSongInteraction


# =========================================================
# FEATURE NAMES
# =========================================================

SONG_FEATURE_NAMES = [
    "song_popularity",
    "song_tempo",
    "song_energy",
    "song_danceability",
    "song_valence",
    "song_acousticness",
    "song_unique_listeners",
    "song_play_count",
    "song_total_listen_time",
    "song_plays_last_24h",
    "song_age_days",
]


USER_PROFILE_FEATURE_NAMES = [
    "profile_avg_tempo",
    "profile_avg_energy",
    "profile_avg_danceability",
    "profile_avg_valence",
    "profile_avg_acousticness",
    "profile_avg_popularity",
    "profile_total_play_count",
    "profile_total_listen_time",
    "profile_avg_completion_rate",
    "profile_avg_skip_rate",
]


SIMILARITY_FEATURE_NAMES = [
    "tempo_distance",
    "energy_distance",
    "danceability_distance",
    "valence_distance",
    "acousticness_distance",
    "popularity_distance",
]


INTERACTION_FEATURE_NAMES = [
    "interaction_play_count",
    "interaction_total_listen_time",
    "interaction_avg_listen_time",
    "interaction_skip_count",
    "interaction_skip_rate",
    "interaction_completed_count",
    "interaction_completion_rate",
    "interaction_engagement_score",
]


# =========================================================
# SONG AGE
# =========================================================

def calculate_song_age_days(
    song: Songs,
) -> float:

    if not song.release_date:
        return 0.0

    release_date = song.release_date

    if isinstance(
        release_date,
        datetime,
    ):
        release_datetime = release_date

    else:
        release_datetime = datetime.combine(
            release_date,
            time.min,
        )

    if timezone.is_naive(
        release_datetime
    ):
        release_datetime = timezone.make_aware(
            release_datetime
        )

    delta = (
        timezone.now()
        - release_datetime
    )

    return max(
        delta.total_seconds()
        / 86400,
        0.0,
    )


# =========================================================
# SONG FEATURES
# =========================================================

def get_song_features(
    song: Songs,
) -> dict:

    return {
        "song_popularity": float(
            song.popularity or 0
        ),

        "song_tempo": float(
            song.tempo or 0
        ),

        "song_energy": float(
            song.energy or 0
        ),

        "song_danceability": float(
            song.danceability or 0
        ),

        "song_valence": float(
            song.valence or 0
        ),

        "song_acousticness": float(
            song.acousticness or 0
        ),

        "song_unique_listeners": int(
            song.unique_listeners or 0
        ),

        "song_play_count": int(
            song.play_count or 0
        ),

        "song_total_listen_time": int(
            song.total_listen_time or 0
        ),

        "song_plays_last_24h": int(
            song.plays_last_24h or 0
        ),

        "song_age_days": calculate_song_age_days(
            song
        ),
    }


# =========================================================
# INTERACTION FEATURES
# =========================================================

def get_user_song_features(
    interaction: UserSongInteraction | None,
) -> dict:

    # -----------------------------------------------------
    # No interaction
    # -----------------------------------------------------

    if interaction is None:

        return {
            "interaction_play_count": 0,

            "interaction_total_listen_time": 0,

            "interaction_avg_listen_time": 0.0,

            "interaction_skip_count": 0,

            "interaction_skip_rate": 0.0,

            "interaction_completed_count": 0,

            "interaction_completion_rate": 0.0,

            "interaction_engagement_score": 0.0,
        }

    # -----------------------------------------------------
    # Existing interaction
    # -----------------------------------------------------

    return {
        "interaction_play_count": int(
            interaction.play_count or 0
        ),

        "interaction_total_listen_time": int(
            interaction.total_listen_time or 0
        ),

        "interaction_avg_listen_time": float(
            interaction.avg_listen_time or 0
        ),

        "interaction_skip_count": int(
            interaction.skip_count or 0
        ),

        "interaction_skip_rate": float(
            interaction.skip_rate or 0
        ),

        "interaction_completed_count": int(
            interaction.completed_count or 0
        ),

        "interaction_completion_rate": float(
            interaction.completion_rate or 0
        ),

        "interaction_engagement_score": float(
            interaction.engagement_score or 0
        ),
    }


# =========================================================
# USER TASTE PROFILE
# =========================================================

def get_user_taste_profile(
    user_id: int,
    exclude_song_id: int | None = None,
) -> dict:

    queryset = (
        UserSongInteraction.objects
        .filter(
            user_id=user_id,
            play_count__gt=0,
        )
        .select_related(
            "song"
        )
    )

    # -----------------------------------------------------
    # Exclude target song
    #
    # Important for training:
    # prevents target-song leakage.
    # -----------------------------------------------------

    if exclude_song_id is not None:

        queryset = queryset.exclude(
            song_id=exclude_song_id
        )

    interactions = list(
        queryset
    )

    # =====================================================
    # DEFAULT PROFILE
    # =====================================================

    if not interactions:

        return {
            "profile_avg_tempo": 120.0,

            "profile_avg_energy": 0.5,

            "profile_avg_danceability": 0.5,

            "profile_avg_valence": 0.5,

            "profile_avg_acousticness": 0.5,

            "profile_avg_popularity": 0.0,

            "profile_total_play_count": 0,

            "profile_total_listen_time": 0,

            "profile_avg_completion_rate": 0.0,

            "profile_avg_skip_rate": 0.0,
        }

    # =====================================================
    # WEIGHTED VALUES
    # =====================================================

    total_weight = 0.0

    weighted_tempo = 0.0

    weighted_energy = 0.0

    weighted_danceability = 0.0

    weighted_valence = 0.0

    weighted_acousticness = 0.0

    weighted_popularity = 0.0

    total_play_count = 0

    total_listen_time = 0

    completion_rates = []

    skip_rates = []

    # =====================================================
    # BUILD PROFILE
    # =====================================================

    for interaction in interactions:

        song = interaction.song

        # -------------------------------------------------
        # Weight
        # -------------------------------------------------

        weight = max(
            float(
                interaction.play_count or 1
            ),
            1.0,
        )

        total_weight += weight

        # -------------------------------------------------
        # Audio preferences
        # -------------------------------------------------

        weighted_tempo += (
            float(
                song.tempo or 0
            )
            * weight
        )

        weighted_energy += (
            float(
                song.energy or 0
            )
            * weight
        )

        weighted_danceability += (
            float(
                song.danceability or 0
            )
            * weight
        )

        weighted_valence += (
            float(
                song.valence or 0
            )
            * weight
        )

        weighted_acousticness += (
            float(
                song.acousticness or 0
            )
            * weight
        )

        weighted_popularity += (
            float(
                song.popularity or 0
            )
            * weight
        )

        # -------------------------------------------------
        # Aggregate behavior
        # -------------------------------------------------

        total_play_count += int(
            interaction.play_count or 0
        )

        total_listen_time += int(
            interaction.total_listen_time or 0
        )

        completion_rates.append(
            float(
                interaction.completion_rate or 0
            )
        )

        skip_rates.append(
            float(
                interaction.skip_rate or 0
            )
        )

    # =====================================================
    # SAFETY
    # =====================================================

    if total_weight == 0:

        total_weight = 1.0

    # =====================================================
    # FINAL PROFILE
    # =====================================================

    return {
        "profile_avg_tempo": (
            weighted_tempo
            / total_weight
        ),

        "profile_avg_energy": (
            weighted_energy
            / total_weight
        ),

        "profile_avg_danceability": (
            weighted_danceability
            / total_weight
        ),

        "profile_avg_valence": (
            weighted_valence
            / total_weight
        ),

        "profile_avg_acousticness": (
            weighted_acousticness
            / total_weight
        ),

        "profile_avg_popularity": (
            weighted_popularity
            / total_weight
        ),

        "profile_total_play_count": (
            total_play_count
        ),

        "profile_total_listen_time": (
            total_listen_time
        ),

        "profile_avg_completion_rate": (
            sum(completion_rates)
            / len(completion_rates)
            if completion_rates
            else 0.0
        ),

        "profile_avg_skip_rate": (
            sum(skip_rates)
            / len(skip_rates)
            if skip_rates
            else 0.0
        ),
    }


# =========================================================
# SIMILARITY FEATURES
# =========================================================

def build_similarity_features(
    song: Songs,
    user_profile: dict,
) -> dict:

    return {
        "tempo_distance": abs(
            float(
                song.tempo or 0
            )
            - user_profile[
                "profile_avg_tempo"
            ]
        ),

        "energy_distance": abs(
            float(
                song.energy or 0
            )
            - user_profile[
                "profile_avg_energy"
            ]
        ),

        "danceability_distance": abs(
            float(
                song.danceability or 0
            )
            - user_profile[
                "profile_avg_danceability"
            ]
        ),

        "valence_distance": abs(
            float(
                song.valence or 0
            )
            - user_profile[
                "profile_avg_valence"
            ]
        ),

        "acousticness_distance": abs(
            float(
                song.acousticness or 0
            )
            - user_profile[
                "profile_avg_acousticness"
            ]
        ),

        "popularity_distance": abs(
            float(
                song.popularity or 0
            )
            - user_profile[
                "profile_avg_popularity"
            ]
        ),
    }


# =========================================================
# BUILD TRAINING FEATURES
# =========================================================

def build_training_features(
    song: Songs,
    interaction: UserSongInteraction | None,
    user_profile: dict,
) -> dict:

    features = {}

    # -----------------------------------------------------
    # Song features
    # -----------------------------------------------------

    features.update(
        get_song_features(
            song
        )
    )

    # -----------------------------------------------------
    # User profile
    # -----------------------------------------------------

    features.update(
        user_profile
    )

    # -----------------------------------------------------
    # Similarity
    # -----------------------------------------------------

    features.update(
        build_similarity_features(
            song=song,
            user_profile=user_profile,
        )
    )

    # -----------------------------------------------------
    # Current song interaction
    # -----------------------------------------------------

    features.update(
        get_user_song_features(
            interaction
        )
    )

    return features


# =========================================================
# FEATURE NAMES
# =========================================================

def get_feature_names():

    return (
        SONG_FEATURE_NAMES
        + USER_PROFILE_FEATURE_NAMES
        + SIMILARITY_FEATURE_NAMES
        + INTERACTION_FEATURE_NAMES
    )