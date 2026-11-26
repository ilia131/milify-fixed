import logging
import os
from pathlib import Path

import joblib
import numpy as np


logger = logging.getLogger(__name__)
MODEL_PATH = Path(os.getenv(
    "MILIFY_ML_MODEL_PATH", str(Path(__file__).resolve().parents[1] / "models" / "recommender.joblib")
))


FEATURE_NAMES = [
    # =====================================================
    # SONG FEATURES
    # =====================================================

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

    # =====================================================
    # USER PROFILE FEATURES
    # =====================================================

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

    # =====================================================
    # SIMILARITY FEATURES
    # =====================================================

    "tempo_distance",
    "energy_distance",
    "danceability_distance",
    "valence_distance",
    "acousticness_distance",
    "popularity_distance",

    # =====================================================
    # INTERACTION FEATURES
    # =====================================================

    "interaction_play_count",
    "interaction_total_listen_time",
    "interaction_avg_listen_time",
    "interaction_skip_count",
    "interaction_skip_rate",
    "interaction_completed_count",
    "interaction_completion_rate",
    "interaction_engagement_score",
]


class RecommendationEngine:

    def __init__(self, model_path=MODEL_PATH):
        self.model = None
        self.feature_names = FEATURE_NAMES.copy()
        if not model_path.is_file():
            logger.warning("Recommendation model is missing; fallback ranking enabled")
            return

        try:
            package = joblib.load(model_path)
            if isinstance(package, dict):
                model = package["model"]
                features = package.get("feature_names", FEATURE_NAMES)
            else:
                model = package
                features = FEATURE_NAMES
            if list(features) != FEATURE_NAMES or not callable(getattr(model, "predict_proba", None)):
                raise ValueError("Invalid recommendation model or feature order")
            self.model = model
        except Exception as error:
            logger.error("Recommendation model could not be loaded (%s)", type(error).__name__)

    @staticmethod
    def normalize(values):

        values = np.asarray(
            values,
            dtype=float,
        )

        if len(values) == 0:
            return values

        min_value = values.min()
        max_value = values.max()

        if max_value == min_value:
            return np.ones(
                len(values)
            )

        return (
            values - min_value
        ) / (
            max_value - min_value
        )

    # =====================================================
    # FALLBACK
    # =====================================================

    def fallback_score(
        self,
        song,
        songs,
    ):

        play_scores = self.normalize(
            [
                s.play_count
                for s in songs
            ]
        )

        listener_scores = self.normalize(
            [
                s.unique_listeners
                for s in songs
            ]
        )

        recent_scores = self.normalize(
            [
                s.plays_last_24h
                for s in songs
            ]
        )

        index = songs.index(
            song
        )

        return float(
            listener_scores[index] * 0.25
            + play_scores[index] * 0.20
            + recent_scores[index] * 0.20
            + song.popularity * 0.15
            + song.energy * 0.10
            + song.danceability * 0.10
        )

    # =====================================================
    # BUILD FEATURES
    # =====================================================

    @staticmethod
    def build_features(
        song,
        user,
    ):

        interaction = (
            song.interaction
        )

        profile = (
            song.user_profile
        )

        # -------------------------------------------------
        # Similarity
        # -------------------------------------------------

        tempo_distance = abs(
            song.tempo
            - profile.avg_tempo
        )

        energy_distance = abs(
            song.energy
            - profile.avg_energy
        )

        danceability_distance = abs(
            song.danceability
            - profile.avg_danceability
        )

        valence_distance = abs(
            song.valence
            - profile.avg_valence
        )

        acousticness_distance = abs(
            song.acousticness
            - profile.avg_acousticness
        )

        popularity_distance = abs(
            song.popularity
            - profile.avg_popularity
        )

        # -------------------------------------------------
        # EXACT 35 FEATURES
        # -------------------------------------------------

        return [

            # 1-11 SONG
            song.popularity,
            song.tempo,
            song.energy,
            song.danceability,
            song.valence,
            song.acousticness,
            song.unique_listeners,
            song.play_count,
            song.total_listen_time,
            song.plays_last_24h,
            song.song_age_days,

            # 12-21 PROFILE
            profile.avg_tempo,
            profile.avg_energy,
            profile.avg_danceability,
            profile.avg_valence,
            profile.avg_acousticness,
            profile.avg_popularity,
            profile.total_play_count,
            profile.total_listen_time,
            profile.avg_completion_rate,
            profile.avg_skip_rate,

            # 22-27 SIMILARITY
            tempo_distance,
            energy_distance,
            danceability_distance,
            valence_distance,
            acousticness_distance,
            popularity_distance,

            # 28-35 INTERACTION
            interaction.play_count,
            interaction.total_listen_time,
            interaction.avg_listen_time,
            interaction.skip_count,
            interaction.skip_rate,
            interaction.completed_count,
            interaction.completion_rate,
            interaction.engagement_score,
        ]

    # =====================================================
    # PREDICT
    # =====================================================

    def predict_song_score(
        self,
        song,
        user,
    ):

        features = self.build_features(
            song,
            user,
        )

        if len(features) != len(
            FEATURE_NAMES
        ):
            raise ValueError(
                "Feature count mismatch: "
                f"expected={len(FEATURE_NAMES)}, "
                f"got={len(features)}"
            )

        if self.model is None:
            return None

        prediction = (
            self.model.predict_proba(
                [features]
            )[0][1]
        )

        return float(
            prediction
        )

    # =====================================================
    # RECOMMEND
    # =====================================================

    def recommend(
        self,
        user,
        songs,
    ):

        results = []

        for song in songs:

            try:
                model_score = self.predict_song_score(song, user)
                if model_score is not None and not np.isfinite(model_score):
                    model_score = None
            except (ValueError, TypeError, IndexError, RuntimeError) as error:
                logger.warning("Recommendation prediction failed (%s)", type(error).__name__)
                model_score = None

            if model_score is None:

                score = (
                    self.fallback_score(
                        song,
                        songs,
                    )
                )

            else:

                score = model_score

            results.append(
                {
                    "song_id": song.song_id,
                    "score": round(
                        score,
                        6,
                    ),
                }
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return results