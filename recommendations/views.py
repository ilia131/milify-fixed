from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services.redis_service import (
    get_user_recommendations,
    set_user_recommendations,
)
from .services.ml.recommand import (
    recommend_for_user,         
    recommend_from_playlist,     
    recommend_suggest      , 
    
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch

from music.models import Songs
from music.serializers import SongPlayerSerializer
from music.models import Songs
from .services.fresh_track import get_fresh_tracks
from functools import lru_cache
import logging

from django.conf import settings
from gensim.models import Word2Vec
import numpy as np
from .services.ml.rerank import rerank_songs


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_track2vec(path):
    try:
        return Word2Vec.load(str(path))
    except (OSError, ValueError, AttributeError, EOFError) as error:
        logger.warning("Track2Vec could not be loaded (%s)", type(error).__name__)
        return None


class Track2VecRecommendView(APIView):
    TOPN = 40
    LIMIT = 20
    MAX_PER_ARTIST = 2

    def get(self, request, song_uuid):

        try:
            song = Songs.objects.prefetch_related("artist").get(unique_id=song_uuid, is_published=True)
        except Songs.DoesNotExist:
            return Response({"error": "Song not found"}, status=404)

        key = str(song.id)
        model = load_track2vec(settings.TRACK2VEC_MODEL_PATH)

        if model is None or key not in model.wv:
            return self._fallback(request, song)

        try:
            similar = model.wv.most_similar(key, topn=self.TOPN)
        except Exception:
            return self._fallback(request, song)

        ids = []
        for item in similar:
            try:
                ids.append(int(item[0]))
            except:
                continue

        if not ids:
            return self._fallback(request, song)

        queryset = Songs.objects.filter(id__in=ids, is_published=True).prefetch_related("artist")

        id_to_song = {s.id: s for s in queryset}

        ranked_songs = []
        for sid in ids:
            s = id_to_song.get(sid)
            if s:
                ranked_songs.append(s)

        ranked_songs = [s for s in ranked_songs if s.id != song.id]

        seen_artists = {}
        final = []

        for s in ranked_songs:
            artists = list(s.artist.all())
            if not artists:
                continue

            allowed = True
            for a in artists:
                if seen_artists.get(a.id, 0) >= self.MAX_PER_ARTIST:
                    allowed = False
                    break

            if not allowed:
                continue

            for a in artists:
                seen_artists[a.id] = seen_artists.get(a.id, 0) + 1

            final.append(s)

            if len(final) >= self.LIMIT:
                break

        if not final:
            return self._fallback(request, song)

        serializer = SongPlayerSerializer(final, many=True, context={"request": request})
        return Response(serializer.data, status=200)

    # ============================================================
    # FALLBACK WITH SongPlayerSerializer
    # ============================================================

    def _fallback(self, request, song):

        limit = self.LIMIT

        if song.genre:
            results = list(
                Songs.objects.filter(genre=song.genre, is_published=True)
                .exclude(id=song.id)
                .prefetch_related("artist")
                .order_by("-play_count")[:limit]
            )
            if results:
                return Response(
                    SongPlayerSerializer(results, many=True, context={"request": request}).data,
                    status=200
                )

        artist_ids = list(song.artist.values_list("id", flat=True))
        if artist_ids:
            results = list(
                Songs.objects.filter(artist__id__in=artist_ids, is_published=True)
                .exclude(id=song.id)
                .prefetch_related("artist")
                .distinct()
                .order_by("-play_count")[:limit]
            )
            if results:
                return Response(
                    SongPlayerSerializer(results, many=True, context={"request": request}).data,
                    status=200
                )

        results = list(
            Songs.objects.filter(is_published=True).exclude(id=song.id)
            .prefetch_related("artist")
            .order_by("-play_count")[:limit]
        )

        return Response(
            SongPlayerSerializer(results, many=True, context={"request": request}).data,
            status=200
        )



# -----------------------------------------------------
# 🔹 بخش For You — نسخه Hybrid (ALS + Track2Vec + Trending)
# -----------------------------------------------------




class ForYouHybridView(APIView):

    permission_classes = [IsAuthenticated]

    def get_main_artist_name(self, song):

        relations = song.trackartist_set.all()

        main_artist = None

        for rel in relations:

            if rel.role == "main":
                main_artist = rel.artist
                break

        if not main_artist and relations:
            main_artist = relations[0].artist

        return (
            main_artist.artistname
            if main_artist
            else None
        )

    def get(self, request):

        user = request.user

        # =====================================================
        # CHECK REDIS CACHE
        # =====================================================

        try:
            cached = get_user_recommendations(
                user.id
            )
        except Exception:
            cached = None

        if cached:

            if isinstance(cached, bytes):
                cached = cached.decode()

            cached_ids = [
                int(x)
                for x in cached.split(",")
                if x
            ]

            if cached_ids:

                cached_songs = list(
                    Songs.objects
                    .filter(
                        id__in=cached_ids,
                        is_published=True,
                    )
                    .prefetch_related(
                        "trackartist_set",
                        "trackartist_set__artist",
                    )
                )

                song_map = {
                    song.id: song
                    for song in cached_songs
                }

                final = [
                    song_map[song_id]
                    for song_id in cached_ids
                    if song_id in song_map
                ]

                if final:

                    serializer = SongPlayerSerializer(
                        final[:20],
                        many=True,
                        context={
                            "request": request
                        },
                    )

                    return Response(
                        serializer.data
                    )

        # =====================================================
        # ML
        # =====================================================

        ml_recs = (
            recommend_for_user(user.id)
            or []
        )

        # =====================================================
        # FRESH
        # =====================================================

        fresh_recs = get_fresh_tracks(
            user,
            limit=10,
        )

        # =====================================================
        # SUGGEST
        # =====================================================

        suggest_recs = (
            recommend_suggest(user)
            or []
        )

        # =====================================================
        # MERGE
        # =====================================================

        candidates = (
            ml_recs
            +
            fresh_recs
            +
            suggest_recs
        )

        song_ids = [
            song.id
            for song in candidates
        ]

        prefetched_songs = {
            song.id: song
            for song in (
                Songs.objects
                .filter(id__in=song_ids)
                .prefetch_related(
                    "trackartist_set",
                    "trackartist_set__artist",
                )
            )
        }

        seen = set()
        final = []

        for song in candidates:

            uid = str(song.unique_id)

            if uid in seen:
                continue

            seen.add(uid)

            final_song = prefetched_songs.get(
                song.id,
                song,
            )

            final.append(final_song)

            if len(final) >= 20:
                break

        # =====================================================
        # FALLBACK
        # =====================================================

        if len(final) < 20:

            needed = 20 - len(final)

            existing_ids = [
                song.id
                for song in final
            ]

            fallback = (
                Songs.objects
                .filter(is_published=True)
                .exclude(id__in=existing_ids)
                .order_by("-release_date")
                .prefetch_related(
                    "trackartist_set",
                    "trackartist_set__artist",
                )[:needed]
            )

            final.extend(
                list(fallback)
            )

        final = final[:20]

        # =====================================================
        # SAVE RECOMMENDATIONS TO REDIS
        # =====================================================

        try:

            set_user_recommendations(
                user.id,
                [
                    song.id
                    for song in final
                ],
                timeout=300,
            )

        except Exception:
            pass

        # =====================================================
        # RESPONSE
        # =====================================================

        serializer = SongPlayerSerializer(
            final,
            many=True,
            context={
                "request": request
            },
        )

        return Response(
            serializer.data
        )


class FreshTracksView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        # اگر درخواست limit داشت
        try:
            limit = int(request.GET.get("limit", 20))
        except ValueError:
            limit = 20

        try:
            songs = get_fresh_tracks(user, limit=limit)
        except Exception as e:
            print("FreshTracks error:", e)
            return Response([], status=200)

        try:
            songs = rerank_songs(user, songs)
        except Exception as e:
            print("Reranker error:", e)

        data = [
            {
                "uuid": str(s.unique_id),
                "title": s.title,
                "artist": getattr(s.artist, "name", None),
                "release_date": s.release_date,
            }
            for s in songs[:limit]
        ]

        return Response(data, status=200)