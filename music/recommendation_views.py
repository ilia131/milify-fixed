from .services.playback import playable_track_url
from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

import requests

from music.models import Songs, MusicCategory

from .recommender_serializers import RecommendationSongSerializer
from .services.recommendation_service import RecommendationService


ML_SERVICE_URL = getattr(
    settings,
    "ML_SERVICE_URL",
    "http://ml-service:8001",
)


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            limit = int(
                request.query_params.get("limit", 10)
            )
        except (TypeError, ValueError):
            limit = 10

        recommendations = (
            RecommendationService.get_recommendations(
                user=request.user,
                limit=limit,
            )
        )

        data = []

        for item in recommendations:
            song = item["song"]

            serialized = RecommendationSongSerializer(
                song,
                context={"request": request},
            ).data

            serialized["score"] = round(
                item["score"],
                6,
            )

            data.append(serialized)

        return Response(
            {
                "count": len(data),
                "recommendations": data,
            }
        )


class CategoryRecommendationsView(APIView):
    """
    Returns AI-ranked songs for every Milify music category.
    """

    permission_classes = [AllowAny]

    # =========================================================
    # USER FEATURES
    # =========================================================

    def get_user_features(self, request):

        if not request.user.is_authenticated:
            return {
                "user_id": 0,
                "avg_listen_time": 0,
                "skip_rate": 0,
                "play_count": 0,
                "favorite_genres": [],
                "favorite_categories": [],
            }

        user = request.user

        interactions = user.song_interactions.all()

        play_count = 0
        total_listen_time = 0
        total_skips = 0

        favorite_categories = []
        favorite_genres = []

        for interaction in interactions:

            play_count += interaction.play_count or 0

            total_listen_time += (
                interaction.total_listen_time or 0
            )

            total_skips += (
                interaction.skip_count or 0
            )

            if interaction.song.category:
                favorite_categories.append(
                    interaction.song.category
                )

            if interaction.song.genre:
                favorite_genres.append(
                    interaction.song.genre.name
                )

        avg_listen_time = (
            total_listen_time / play_count
            if play_count > 0
            else 0
        )

        skip_rate = (
            total_skips / play_count
            if play_count > 0
            else 0
        )

        return {
            "user_id": user.id,
            "avg_listen_time": avg_listen_time,
            "skip_rate": skip_rate,
            "play_count": play_count,
            "favorite_genres": list(
                set(favorite_genres)
            ),
            "favorite_categories": list(
                set(favorite_categories)
            ),
        }

    # =========================================================
    # SONG FEATURES FOR ML
    # =========================================================

    def get_song_features(self, songs):

        song_features = []

        for song in songs:

            age_days = (
                (
                    timezone.now()
                    - song.release_date
                ).total_seconds()
                / 86400
                if song.release_date
                else 0
            )

            song_features.append(
                {
                    "song_id": song.id,
                    "popularity": song.popularity or 0,
                    "tempo": song.tempo or 120,
                    "energy": song.energy or 0.5,
                    "danceability": (
                        song.danceability or 0.5
                    ),
                    "valence": song.valence or 0,
                    "acousticness": (
                        song.acousticness or 0
                    ),
                    "unique_listeners": (
                        song.unique_listeners or 0
                    ),
                    "play_count": song.play_count or 0,
                    "total_listen_time": (
                        song.total_listen_time or 0
                    ),
                    "plays_last_24h": (
                        song.plays_last_24h or 0
                    ),
                    "song_age_days": max(
                        age_days,
                        0,
                    ),
                }
            )

        return song_features

    # =========================================================
    # CALL ML SERVICE
    # =========================================================

    def call_ml_service(
        self,
        user_features,
        songs,
    ):

        payload = {
            "user": user_features,
            "songs": self.get_song_features(
                songs
            ),
        }

        try:

            response = requests.post(
                f"{ML_SERVICE_URL}/recommend",
                json=payload,
                timeout=5,
            )

            response.raise_for_status()

            data = response.json()

            return data.get(
                "recommendations",
                [],
            )

        except requests.RequestException:
            return []

    # =========================================================
    # FILE URL
    # =========================================================

    def get_file_url(
        self,
        request,
        field,
    ):

        if not field:
            return None

        try:
            url = field.url
        except (ValueError, AttributeError):
            return None

        if not url:
            return None

        if (
            url.startswith("http://")
            or url.startswith("https://")
        ):
            return url

        return request.build_absolute_uri(url)

    # =========================================================
    # SONG SERIALIZER
    # =========================================================

    def serialize_song(
        self,
        request,
        song,
        score=0,
    ):

        artists = list(
            song.artist.all()
        )

        track_url = playable_track_url(song, request)
        return {
            # ---------------------------------------------
            # Basic
            # ---------------------------------------------

            "id": song.id,

            "unique_id": str(
                song.unique_id
            ),

            "title": song.title,

            "description": song.description,

            "duration": song.duration,

            # ---------------------------------------------
            # Artist
            # ---------------------------------------------

            "artistname": (
                artists[0].artistname
                if artists
                else None
            ),

            "artists": [
                artist.artistname
                for artist in artists
            ],

            "artist": [
                {
                    "id": artist.id,
                    "name": artist.artistname,
                }
                for artist in artists
            ],

            # ---------------------------------------------
            # Media
            # ---------------------------------------------

            "image": self.get_file_url(
                request,
                song.image,
            ),

            "image_url": self.get_file_url(
                request,
                song.image,
            ),

            "track": track_url,

            "track_url": track_url,

            # ---------------------------------------------
            # Music information
            # ---------------------------------------------

            "genre": (
                song.genre.name
                if song.genre
                else None
            ),

            "genre_name": (
                song.genre.name
                if song.genre
                else None
            ),

            "category": song.category,

            "album": (
                song.album.id
                if song.album
                else None
            ),

            "album_name": (
                song.album.title
                if song.album
                else None
            ),

            # ---------------------------------------------
            # ML / statistics
            # ---------------------------------------------

            "score": round(
                float(score or 0),
                6,
            ),

            "play_count": (
                song.play_count or 0
            ),

            "popularity": (
                song.popularity or 0
            ),

            "unique_listeners": (
                song.unique_listeners or 0
            ),

            "plays_last_24h": (
                song.plays_last_24h or 0
            ),

            "total_listen_time": (
                song.total_listen_time or 0
            ),

            # ---------------------------------------------
            # Audio features
            # ---------------------------------------------

            "tempo": song.tempo,

            "energy": song.energy,

            "danceability": song.danceability,

            "valence": song.valence,

            "acousticness": song.acousticness,

            "loudness": song.loudness,

            "audio_features": {},

            # ---------------------------------------------
            # Other
            # ---------------------------------------------

            "verified": song.verified,

            "is_published": song.is_published,

            "is_subscription_only": (
                song.is_subscription_only
                if hasattr(
                    song,
                    "is_subscription_only",
                )
                else False
            ),

            "release_date": (
                song.release_date
            ),

            "track_number": (
                song.track_number
                if hasattr(
                    song,
                    "track_number",
                )
                else None
            ),

            "lyrics": [],

            "shorts": [],

            "total_revenue": "0.00",

            "is_liked": False,
        }

    # =========================================================
    # GET
    # =========================================================

    def get(self, request):

        user_features = (
            self.get_user_features(
                request
            )
        )

        response_data = {}

        # =====================================================
        # ALL MILIFY CATEGORIES
        # =====================================================

        for category in MusicCategory.values:

            songs = list(
                Songs.objects
                .filter(
                    category=category,
                    is_published=True,
                )
                .select_related(
                    "genre",
                    "album",
                )
                .prefetch_related(
                    "artist",
                )
                .order_by(
                    "-play_count"
                )[:100]
            )

            # =================================================
            # EMPTY CATEGORY
            # =================================================

            if not songs:

                response_data[category] = {
                    "category": category,
                    "count": 0,
                    "songs": [],
                }

                continue

            # =================================================
            # AI RANKING
            # =================================================

            recommendations = (
                self.call_ml_service(
                    user_features=user_features,
                    songs=songs,
                )
            )

            # =================================================
            # SCORE MAP
            # =================================================

            score_map = {
                item["song_id"]: item["score"]
                for item in recommendations
                if (
                    "song_id" in item
                    and "score" in item
                )
            }

            # =================================================
            # SORT
            # =================================================

            ranked_songs = sorted(
                songs,
                key=lambda song: score_map.get(
                    song.id,
                    0,
                ),
                reverse=True,
            )

            # =================================================
            # RESPONSE
            # =================================================

            response_data[category] = {
                "category": category,

                "count": len(
                    ranked_songs
                ),

                "songs": [
                    self.serialize_song(
                        request=request,
                        song=song,
                        score=score_map.get(
                            song.id,
                            0,
                        ),
                    )
                    for song in ranked_songs
                ],
            }

        return Response(
            response_data
        )
