from uuid import UUID

from subscriptions.access import song_subscription_access
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Songs , Album , LikedSong , Playlist , PlaylistTrack , Genre
from .serializers import SongPlayerSerializer , AlbumSerializer , ShortVideoDetailSerializer , Album2Serializer, ShortVideo2Serializer , BigCardArtistSerializer , LikedSongSerializer , PlaylistSerializer , GenreBrowseSerializer , GenreDetailSerializer , Song2Serializer
from music.services.recommendation import get_fresh_tracks ,get_trending_tracks , register_listen , get_popular_albums
from uuid import UUID
from users.authentication import CustomJWTAuthentication

from django.db.models.functions import (
    Now,
    Extract,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import (
    Count, F, FloatField, Value, IntegerField,
    ExpressionWrapper, Case, When

)
from django.db.models.functions import Now, ExtractHour, NullIf
from recentlyplayed.models import RecentlyPlayed
from rest_framework.generics import ListAPIView , RetrieveAPIView
from .models import ShortVideo
from .serializers import ShortVideoSerializer
from .pagination import ExplorePagination
from django.db.models import Prefetch

from .models import Songs, TrackArtist
from .serializers import SongSerializer
from artists.models import Artist
from rest_framework.permissions import IsAuthenticated
from .permissions import IsArtist
from rest_framework import generics

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from django.utils import timezone

from django.db.models import Sum, F
import math

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import viewsets, status

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank , TrigramSimilarity 
from django.db.models import Q

from .models import Songs
from artists.models import Artist

from .serializers import SongPlayerSerializer
from artists.serializers import ArtistSerializer

from .pagination import SongSearchPagination , ArtistSearchPagination , GenreBrowsePagination , GenreSongsPagination
from django.db.models.functions import Coalesce, Cast
from urllib.parse import unquote

from music.services.recommendation import register_skip
from django.db import transaction
from .models import (
    ShortVideo,
    ShortVideoComment,
)

from .serializers import (
    ShortVideoCommentSerializer,
)

class ShortVideoLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, uuid):
        short_video = get_object_or_404(
            ShortVideo,
            uuid=uuid
        )

        user = request.user

        with transaction.atomic():

            if short_video.likes.filter(
                id=user.id
            ).exists():

                short_video.likes.remove(user)

                liked = False

            else:

                short_video.likes.add(user)

                liked = True

        return Response(
            {
                "liked": liked,
                "likes_count": short_video.likes.count(),
            },
            status=status.HTTP_200_OK,
        )
        
class ShortVideoCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        short_video = get_object_or_404(
            ShortVideo,
            uuid=uuid
        )

        comments = (
            ShortVideoComment.objects
            .filter(
                short_video=short_video,
                parent__isnull=True,
            )
            .select_related("user")
            .prefetch_related("likes")
        )

        serializer = ShortVideoCommentSerializer(
            comments,
            many=True,
            context={"request": request},
        )

        return Response(
            {
                "count": short_video.comments_count,
                "results": serializer.data,
            }
        )

    def post(self, request, uuid):
        short_video = get_object_or_404(
            ShortVideo,
            uuid=uuid
        )

        if not short_video.allow_comments:
            return Response(
                {
                    "detail": "Comments are disabled for this video."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        text = request.data.get("text", "").strip()

        if not text:
            return Response(
                {
                    "detail": "Comment cannot be empty."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(text) > 1000:
            return Response(
                {
                    "detail": "Comment cannot exceed 1000 characters."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        parent_id = request.data.get("parent")

        parent = None

        if parent_id:
            parent = get_object_or_404(
                ShortVideoComment,
                id=parent_id,
                short_video=short_video,
            )

        with transaction.atomic():

            comment = ShortVideoComment.objects.create(
                short_video=short_video,
                user=request.user,
                text=text,
                parent=parent,
            )

            short_video.comments_count += 1

            short_video.save(
                update_fields=["comments_count"]
            )

        serializer = ShortVideoCommentSerializer(
            comment,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
        
class ShortVideoCommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id):

        comment = get_object_or_404(
            ShortVideoComment,
            id=comment_id
        )

        if comment.user_id != request.user.id:
            return Response(
                {
                    "detail": "You can only delete your own comments."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        short_video = comment.short_video

        with transaction.atomic():

            comment.delete()

            if short_video.comments_count > 0:
                short_video.comments_count -= 1

                short_video.save(
                    update_fields=["comments_count"]
                )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class ShortVideoCommentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):

        comment = get_object_or_404(
            ShortVideoComment,
            id=comment_id
        )

        user = request.user

        if comment.likes.filter(
            id=user.id
        ).exists():

            comment.likes.remove(user)

            liked = False

        else:

            comment.likes.add(user)

            liked = True

        return Response(
            {
                "liked": liked,
                "likes_count": comment.likes.count(),
            }
        )

class ShortVideoShareView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, uuid):

        short_video = get_object_or_404(
            ShortVideo,
            uuid=uuid
        )

        short_video.shares_count += 1

        short_video.save(
            update_fields=["shares_count"]
        )

        return Response(
            {
                "shares_count": short_video.shares_count
            },
            status=status.HTTP_200_OK,
        )
class ArtistSongCreate2View(generics.CreateAPIView):

    serializer_class = Song2Serializer
    permission_classes = [IsAuthenticated, IsArtist]

    @transaction.atomic
    def perform_create(self, serializer):

        song = serializer.save()

        TrackArtist.objects.create(
            track=song,
            artist=self.request.user.artist_profile,
            role="main",
        )


class SongSkipView(APIView):

    def post(self, request, unique_id):

        session_id = request.data.get("session_id")

        if not session_id:
            return Response(
                {
                    "error": "session_id is required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            listen, skipped = register_skip(
                user=request.user,
                session_id=session_id,
            )

        except ValidationError as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "status": "ok",
                "song_id": str(
                    listen.song.unique_id
                ),
                "session_id": str(session_id),
                "skipped": skipped,
                "skip_counted": listen.skip_counted,
            },
            status=status.HTTP_200_OK,
        )
class AlbumListView(ListAPIView):
    serializer_class = AlbumSerializer

    def get_queryset(self):
        return (
            Album.objects
            .select_related("artist")
            .order_by("-release_date")
        )
class BrowseGenresView(APIView):

    @method_decorator(cache_page(60 * 10))
    def get(self, request, name=None):

        # ========= DETAIL =========
        if name:

            name = unquote(name)

            genre = get_object_or_404(
                Genre.objects.annotate(
                    songs_count=Count(
                        "songs",
                        filter=Q(songs__is_published=True)
                    )
                ),
                name__iexact=name
            )

            songs = (
                Songs.objects.filter(
                    genre=genre,
                    is_published=True
                )
                .select_related("genre", "album")
                .prefetch_related("artist")
                .order_by("-plays_last_24h", "-play_count", "-id")
            )

            paginator = GenreSongsPagination()
            paginated_songs = paginator.paginate_queryset(songs, request, view=self)

            return Response({
                "genre": GenreDetailSerializer(
                    genre,
                    context={"request": request}
                ).data,

                "songs": paginator.get_paginated_response(
                    SongPlayerSerializer(
                        paginated_songs,
                        many=True,
                        context={"request": request}
                    ).data
                ).data
            })

        # ========= BROWSE =========
        genres = (
            Genre.objects.annotate(
                songs_count=Count(
                    "songs",
                    filter=Q(songs__is_published=True)
                )
            )
            .filter(songs_count__gt=0)
            .order_by("-songs_count")
        )

        serializer = GenreBrowseSerializer(
            genres,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)






class GlobalSearchView(APIView):

    def get(self, request):

        q = request.GET.get("q", "")
        genre = request.GET.get("genre")

        songs = (
            Songs.objects
            .filter(is_published=True)
            .select_related("genre", "album")
            .prefetch_related("artist")
        )

        artists = Artist.objects.all()

        if genre:
            songs = songs.filter(genre__name__icontains=genre)

        if q:

            vector = (
                SearchVector("title", weight="A") +
                SearchVector("artist__artistname", weight="A") +
                SearchVector("genre__name", weight="B") +
                SearchVector("description", weight="C")
            )

            query = SearchQuery(q)

            songs = songs.annotate(
                rank=SearchRank(vector, query),
                similarity=(
                    TrigramSimilarity("title", q) +
                    TrigramSimilarity("artist__artistname", q)
                )
            ).filter(
                Q(rank__gte=0.1) |
                Q(similarity__gt=0.2)
            ).order_by(
                "-rank",
                "-similarity",
                "-plays_last_24h",
                "-play_count",
                "-id"
            ).distinct()

            artists = artists.annotate(

                similarity=(
                    TrigramSimilarity("artistname", q) +
                    TrigramSimilarity("bio", q)
                ),

                total_play_count=Coalesce(
                    Sum("tracks__play_count", distinct=True), 0
                ),

                monthly_listeners_calc=Coalesce(
                    Sum("tracks__unique_listeners", distinct=True), 0
                )

            ).filter(
                Q(artistname__icontains=q) |
                Q(similarity__gt=0.2)
            ).order_by(
                "-is_featured",
                "-similarity",
                "-monthly_listeners_calc",
                "-total_play_count",
                "-id"
            ).distinct()

        else:

            songs = songs.order_by(
                "-plays_last_24h",
                "-play_count",
                "-id"
            )

            artists = artists.annotate(

                total_play_count=Coalesce(
                    Sum("tracks__play_count", distinct=True), 0
                ),

                monthly_listeners_calc=Coalesce(
                    Sum("tracks__unique_listeners", distinct=True), 0
                )

            ).order_by(
                "-is_featured",
                "-monthly_listeners_calc",
                "-created_at",
                "-id"
            )

        # ---------- TOP RESULT ----------
        top_song = songs.first()
        top_artist = artists.first()

        top_result = None

        if top_song and (
            not top_artist or
            top_song.play_count >= (top_artist.total_play_count or 0)
        ):
            top_result = SongPlayerSerializer(
                top_song,
                context={"request": request}
            ).data
            top_result["type"] = "song"

        elif top_artist:
            top_result = ArtistSerializer(
                top_artist,
                context={"request": request}
            ).data
            top_result["type"] = "artist"

        # ---------- PAGINATION ----------

        song_paginator = SongSearchPagination()
        artist_paginator = ArtistSearchPagination()

        songs_page = song_paginator.paginate_queryset(songs, request, view=self)
        artists_page = artist_paginator.paginate_queryset(artists, request, view=self)

        songs_data = SongPlayerSerializer(
            songs_page,
            many=True,
            context={"request": request}
        ).data

        artists_data = ArtistSerializer(
            artists_page,
            many=True,
            context={"request": request}
        ).data

        return Response({

            "top_result": top_result,

            "songs": song_paginator.get_paginated_response(
                songs_data
            ).data,

            "artists": artist_paginator.get_paginated_response(
                artists_data
            ).data

        })


class SongsByGenreView(APIView):

    def get(self, request):

        genre_name = request.GET.get("genre")

        songs = (
            Songs.objects
            .filter(is_published=True)
            .select_related("genre", "album")
            .prefetch_related("artist")
        )

        if genre_name:
            songs = songs.filter(genre__name__icontains=genre_name)

        songs = songs.order_by("-plays_last_24h", "-play_count")

        serializer = SongPlayerSerializer(
            songs,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)
    
#PlayLIST
class PlaylistViewSet(viewsets.ModelViewSet):
    
    permission_classes = [IsAuthenticated]
    serializer_class = PlaylistSerializer
    lookup_field = 'unique_id' 

    def get_queryset(self):

        # فقط پلی‌لیست‌های همین کاربر
        return Playlist.objects.filter(user=self.request.user).prefetch_related(
            'playlisttrack_set__song'
        )

    def get_object(self):
        queryset = self.get_queryset()
        unique_id = self.kwargs.get(self.lookup_field)
        
        return get_object_or_404(queryset, unique_id=unique_id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='add-track')
    def add_track(self, request, unique_id=None):
        playlist = self.get_object()
        song_uuid = request.data.get('song_uuid')
        
        if not song_uuid:
            return Response({"error": "song_uuid is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        song = get_object_or_404(Songs, unique_id=song_uuid)
        
        if PlaylistTrack.objects.filter(playlist=playlist, song=song).exists():
            return Response({"detail": "Song already in playlist"}, status=status.HTTP_400_BAD_REQUEST)

        last_pos = PlaylistTrack.objects.filter(playlist=playlist).count()
        
        PlaylistTrack.objects.create(
            playlist=playlist,
            song=song,
            position=last_pos + 1
        )
        
        return Response({"detail": "Track added successfully"}, status=status.HTTP_201_CREATED)

    # --- اکشن حذف کردن آهنگ ---
    @action(detail=True, methods=['post'], url_path='remove-track')
    def remove_track(self, request, unique_id=None):
        playlist = self.get_object()
        song_uuid = request.data.get('song_uuid')
        
        track_entry = PlaylistTrack.objects.filter(playlist=playlist, song__unique_id=song_uuid)
        
        if track_entry.exists():
            track_entry.delete()
            return Response({"detail": "Track removed"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Track not found in this playlist"}, status=status.HTTP_404_NOT_FOUND)


#LIKED
class LikedStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ids_param = request.GET.get("ids")

        if not ids_param:
            return Response({})

        try:
            unique_ids = [UUID(i) for i in ids_param.split(",")]
        except ValueError:
            return Response({"error": "Invalid UUID format"}, status=400)

        liked_ids = set(
            LikedSong.objects.filter(
                user=request.user,
                song__unique_id__in=unique_ids
            ).values_list("song__unique_id", flat=True)
        )

        result = {
            str(uid): uid in liked_ids
            for uid in unique_ids
        }

        return Response(result)


class ToggleLikeSong(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, song_id):
        user = request.user

        try:
            song = Songs.objects.get(unique_id=song_id)
        except Songs.DoesNotExist:
            return Response({"detail": "Song not found"}, status=404)

        liked = LikedSong.objects.filter(user=user, song=song)

        if liked.exists():
            liked.delete()
            return Response({"liked": False})

        LikedSong.objects.create(user=user, song=song)
        return Response({"liked": True})


class LikedSongsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            LikedSong.objects.filter(user=request.user)
            .select_related("song")
            .prefetch_related("song__artist")
            .order_by("-created_at")
        )

        serializer = LikedSongSerializer(qs, many=True, context={"request": request})

        return Response(serializer.data)
#ALBUMS
class AlbumTracksView(APIView):

    def get(self, request, artist_name, album_title):
        try:
            artist = Artist.objects.get(artistname__iexact=artist_name)
        except Artist.DoesNotExist:
            return Response(
                {"detail": "Artist not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            album = Album.objects.get(
                title__iexact=album_title,
                artist=artist
            )
        except Album.DoesNotExist:
            return Response(
                {"detail": "Album not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AlbumSerializer(album, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)








class BigCardArtistView(APIView):

    def get(self, request):
        artists = Artist.objects.all()

        results = []

        for artist in artists:
            tracks = artist.tracks.all()

            score = 0

            for track in tracks:
                score += track.plays_last_24h * 2
                score += track.play_count * 0.3
                score += track.unique_listeners * 0.5

                days = (timezone.now() - track.release_date).days
                freshness = max(0, 100 - days)
                score += freshness

            results.append({
                "artist": artist,
                "score": score
            })

        results = sorted(results, key=lambda x: x["score"], reverse=True)

        output = []
        for item in results:
            serializer = BigCardArtistSerializer(
                item["artist"],
                context={"request": request}     # مشکل شما همین یک خط بود
            )
            data = serializer.data
            data["score"] = item["score"]
            output.append(data)

        return Response(output)

#SHORTVIDEO EXPLORER
# class ExploreShortVideoView(ListAPIView):
#     serializer_class = ShortVideoSerializer
#     pagination_class = ExplorePagination

#     @method_decorator(cache_page(60))
#     def get(self, *args, **kwargs):
#         return super().get(*args, **kwargs)





@api_view(["GET"])
def fresh_tracks(request):
    
    songs = get_fresh_tracks(request.user)

    serializer = SongPlayerSerializer(
        songs,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)


class SongDetailView(generics.RetrieveAPIView):
    serializer_class = SongPlayerSerializer
    lookup_field = "unique_id"

    queryset = (
        Songs.objects
        .select_related("genre", "album")
        .prefetch_related(
            "trackartist_set__artist",
            "lyrics_lines",
            "short_videos",
            "liked_by",
        )
    )



class PopularAlbumsView(APIView):
    def get(self, request):

        try:
            limit = int(request.query_params.get("limit", 20))
        except (TypeError, ValueError):
            limit = 20

        albums = get_popular_albums(limit=limit)

        serializer = AlbumSerializer(
            albums,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def trending_tracks(request):
    songs = get_trending_tracks(limit=20)
    serializer = SongPlayerSerializer(
        songs,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)

class SongPlayerView(APIView):

    def get(self, request, unique_id):
        song = get_object_or_404(Songs, unique_id=unique_id)

        serializer = SongPlayerSerializer(song, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)


def add_recent_play(user, song):
    RecentlyPlayed.objects.update_or_create(
        user=user,
        song=song,
        defaults={"played_at": timezone.now()}
    )


from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class SongListenView(APIView):

    def post(self, request, unique_id):

        try:
            seconds = int(
                request.data.get("seconds", 0)
            )
        except (TypeError, ValueError):
            seconds = 0

        try:
            session_id = UUID(str(request.data.get("session_id")))
        except ValueError:
            return Response(
                {
                    "error": "A valid session_id is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        song = get_object_or_404(
            Songs,
            unique_id=unique_id
        )

        if not song_subscription_access(song, request.user)["can_play"]:
            return Response(
                {"detail": "A current subscription is required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:

            listen, play_counted = register_listen(
                song=song,
                user=request.user,
                seconds=seconds,
                session_id=session_id,
            )

        except ValidationError as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # فقط زمانی که Play واقعاً ثبت شد
        # Recently Played را آپدیت کن
        if play_counted and request.user.is_authenticated:
            add_recent_play(
                request.user,
                song
            )

        return Response(
            {
                "status": "ok",
                "song_id": str(song.unique_id),
                "seconds_listened": (
                    listen.seconds_listened
                    if listen
                    else 0
                ),
                "play_counted": play_counted,
                "session_id": str(session_id),
            },
            status=status.HTTP_200_OK
        )



@api_view(["GET"])
def trending_tracks_view(request):

    user = request.user

    songs = get_trending_tracks(user=user, limit=20)

    serializer = SongPlayerSerializer(songs, many=True, context={"request": request})

    return Response(serializer.data)





class AlbumSearchView(APIView):

    def get(self, request):
        title = request.query_params.get("title")
        artist = request.query_params.get("artist")

        albums = Album.objects.all()

        if title:
            albums = albums.filter(title__icontains=title)

        if artist:
            albums = albums.filter(artist__artistname__icontains=artist)

        albums = albums.prefetch_related("tracks")

        serializer = AlbumSerializer(
            albums,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)





class ExploreShortVideoView(ListAPIView):
    serializer_class = ShortVideoSerializer
    pagination_class = ExplorePagination

    def get_queryset(self):

        artist_id = self.request.query_params.get("artist")

        qs = (
            ShortVideo.objects.all()
            .select_related("main_artist")
            .prefetch_related("likes")
        )

        if artist_id:
            qs = qs.filter(main_artist__id=artist_id)

        qs = qs.annotate(

            # ========================
            # BASIC COUNTS
            # ========================

            likes_total=Count("likes", distinct=True),

            safe_views=ExpressionWrapper(
                F("views") + Value(1.0),
                output_field=FloatField(),
            ),

            safe_duration=ExpressionWrapper(
                F("duration") + Value(0.1),
                output_field=FloatField(),
            ),

            # ========================
            # WATCH RATIO
            # ========================

            watch_ratio=ExpressionWrapper(
                F("watch_time") /
                (F("safe_views") * F("safe_duration")),
                output_field=FloatField(),
            ),

            # ========================
            # ENGAGEMENT SCORE
            # ========================

            engagement=ExpressionWrapper(
                (
                    Value(0.4) *
                    (F("likes_total") / F("safe_views"))
                ) +
                (
                    Value(0.3) *
                    (F("comments_count") / F("safe_views"))
                ) +
                (
                    Value(0.3) *
                    (F("shares_count") / F("safe_views"))
                ),
                output_field=FloatField(),
            ),

            # ========================
            # AGE IN HOURS
            # ========================
            # PostgreSQL:
            # interval -> seconds -> hours

            age_hours=ExpressionWrapper(
                Extract(
                    Now() - F("created_at"),
                    "epoch",
                ) / Value(3600.0),
                output_field=FloatField(),
            ),

            # ========================
            # FRESHNESS DECAY
            # ========================

            freshness=ExpressionWrapper(
                Value(1.0) /
                (
                    Value(1.0) +
                    (F("age_hours") / Value(12.0))
                ),
                output_field=FloatField(),
            ),
        )

        # ========================
        # FINAL SCORE
        # ========================

        qs = qs.annotate(

            final_score=ExpressionWrapper(

                (
                    Value(0.5) * F("watch_ratio")
                ) +
                (
                    Value(0.3) * F("engagement")
                ) +
                (
                    Value(0.2) * F("freshness")
                ),

                output_field=FloatField(),
            )
        )

        return qs.order_by("-final_score")

class ShortVideoDetailView(RetrieveAPIView):
    queryset = ShortVideo.objects.all()
    serializer_class = ShortVideoDetailSerializer
    lookup_field = "uuid"
    
    
    

#ADMIN PANEL

class ArtistAlbumCreateView(generics.CreateAPIView):

    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated, IsArtist]

    def perform_create(self, serializer):
        serializer.save(artist=self.request.user.artist_profile)
        





class ArtistSongCreateView(generics.CreateAPIView):

    serializer_class = SongSerializer
    permission_classes = [IsAuthenticated, IsArtist]

    def perform_create(self, serializer):

        song = serializer.save()

        TrackArtist.objects.create(
            track=song,
            artist=self.request.user.artist_profile,
            role="main"
        )


class ArtistShortCreateView(generics.CreateAPIView):

    serializer_class = ShortVideo2Serializer
    permission_classes = [IsAuthenticated, IsArtist]

    def perform_create(self, serializer):

        serializer.save(
            user=self.request.user,
            main_artist=self.request.user.artist_profile
        )
        


class ArtistAlbumListView(generics.ListAPIView):

    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated, IsArtist]

    def get_queryset(self):
        return Album.objects.filter(
            artist=self.request.user.artist_profile
        )
        

class ArtistSongListView(generics.ListAPIView):

    serializer_class = SongSerializer
    permission_classes = [IsAuthenticated, IsArtist]

    def get_queryset(self):
        return Songs.objects.filter(
            trackartist__artist=self.request.user.artist_profile
        )


class ArtistShortListView(generics.ListAPIView):

    serializer_class = ShortVideo2Serializer
    permission_classes = [IsAuthenticated, IsArtist]

    def get_queryset(self):
        return ShortVideo.objects.filter(
            main_artist=self.request.user.artist_profile
        )
        
        

class ArtistAlbumsView(APIView):
    permission_classes = [IsAuthenticated , IsArtist]

    def get(self, request):
        artist = request.user.artist_profile  

        albums = Album.objects.filter(artist=artist)

        serializer = Album2Serializer(albums, many=True)

        return Response(serializer.data)