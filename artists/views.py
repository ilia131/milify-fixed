from django.utils import timezone

from rest_framework import generics
from .models import Artist
from .serializers import ArtistSerializer , ArtistListSerializer , FollowArtistSerializer
from django.utils import timezone
from rest_framework.generics import ListAPIView


import os
from django.db.models.functions import (
    Coalesce,
    Least,
    Log,
    Exp,
    ExtractDay,
    Extract,
)
from django.db.models import (
    Sum,
    Count,
    Q,
    F,
    Value,
    FloatField,
    Case,
    When,
    ExpressionWrapper,
    Max,   
)
import re
from django.http import StreamingHttpResponse, HttpResponse
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

from music.serializers import SongPlayerSerializer , AlbumSerializer
from .alghoritms.artist_ranking import get_ranked_artist_songs  , get_ranked_artist_albums



from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from artists.models import Artist
from artists.serializers import ArtistSerializer
from .pagination import ArtistSongsPagination , ArtistAlbumsPagination

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ArtistCreateSerializer , ArtistUpdateSerializer , ArtistDashboardSerializer
from rest_framework.permissions import AllowAny

from .models import Artist, FollowArtist
from django.db.models.functions import TruncDate

class ArtistFollowerChart(APIView):

    def get(self, request, artistname):

        artist = get_object_or_404(
            Artist,
            artistname=artistname
        )

        data = (
            FollowArtist.objects
            .filter(artist=artist)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .order_by("date")
        )

        result = {}

        for item in data:
            date = str(item["date"])
            result[date] = result.get(date, 0) + 1

        chart = [
            {
                "date": date,
                "followers": followers,
            }
            for date, followers in result.items()
        ]

        return Response(chart)
class ArtistDashboardView(APIView):

    def get(self, request, artistname):

        artist = get_object_or_404(
            Artist,
            artistname=artistname
        )

        serializer = ArtistDashboardSerializer(
            artist,
            context={"request": request}
        )

        return Response(serializer.data)
class ArtistUpdateAPIView2(generics.RetrieveUpdateAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistUpdateSerializer
    permission_classes = [AllowAny]
    lookup_field = "artistname"
class ArtistCreateAPIView(generics.CreateAPIView):
    queryset = Artist.objects.all()
    
    serializer_class = ArtistCreateSerializer
    permission_classes = [AllowAny]
    


class ArtistUpdateAPIView(generics.UpdateAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistCreateSerializer

class ArtistSongsView(ListAPIView):
    serializer_class = SongPlayerSerializer
    pagination_class = ArtistSongsPagination

    def get_queryset(self):
        artistname = self.kwargs["artistname"]

        return get_ranked_artist_songs(artistname)


class ArtistAlbumsView(ListAPIView):
    serializer_class = AlbumSerializer
    pagination_class = ArtistAlbumsPagination

    def get_queryset(self):
        artistname = self.kwargs["artistname"]

        return get_ranked_artist_albums(artistname)






@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_follow_artist(request, artist_uuid):

    try:
        artist = Artist.objects.get(uuid=artist_uuid)
    except Artist.DoesNotExist:
        return Response({"error": "Artist not found"}, status=404)

    follow, created = FollowArtist.objects.get_or_create(
        user=request.user,
        artist=artist
    )

    if not created:
        follow.delete()
        return Response({
            "status": "unfollowed"
        })

    return Response({
        "status": "followed"
    })



@api_view(["GET"])
def artist_followers(request, artist_uuid):

    try:
        artist = Artist.objects.get(uuid=artist_uuid)
    except Artist.DoesNotExist:
        return Response({"error": "Artist not found"}, status=404)

    followers = FollowArtist.objects.filter(artist=artist)

    return Response({
        "followers_count": followers.count()
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def is_following(request, artist_uuid):

    is_following = FollowArtist.objects.filter(
        user=request.user,
        artist__uuid=artist_uuid
    ).exists()

    return Response({
        "is_following": is_following
    })



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_following_artists(request):

    follows = FollowArtist.objects.filter(
        user=request.user
    ).select_related("artist")

    serializer = FollowArtistSerializer(follows, many=True)

    return Response(serializer.data)

class UserFavoriteArtistsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        favorite_artists = user.favorite_artists.all()
        serializer = ArtistSerializer(
            favorite_artists,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        artistname = request.data.get("artistname")

        if not artistname:
            return Response(
                {"error": "artistname is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        artist = get_object_or_404(Artist, artistname=artistname)
        user = request.user

        if user.favorite_artists.filter(pk=artist.pk).exists():
            return Response(
                {"detail": f"'{artistname}' is already in favorites."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.favorite_artists.add(artist)
        return Response(
            {"detail": f"'{artistname}' added to favorites successfully."},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request):
        artistname = request.data.get("artistname")

        if not artistname:
            return Response(
                {"error": "artistname is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        artist = get_object_or_404(Artist, artistname=artistname)
        user = request.user

        if not user.favorite_artists.filter(pk=artist.pk).exists():
            return Response(
                {"error": f"'{artistname}' not found in favorites."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.favorite_artists.remove(artist)
        return Response(
            {"detail": f"'{artistname}' removed from favorites."},
            status=status.HTTP_200_OK,
        )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from artists.models import Artist






# class ArtistListView(ListAPIView):
#     queryset = Artist.objects.all()
#     serializer_class = ArtistListSerializer
class ArtistListView(generics.ListAPIView):
    serializer_class = ArtistSerializer

    def get_queryset(self):
        now = timezone.now()
        d7 = now - timezone.timedelta(days=7)
        d14 = now - timezone.timedelta(days=14)
        d28 = now - timezone.timedelta(days=28)

        qs = Artist.objects.all()

        genre_id = self.request.query_params.get('genre_id')
        if genre_id:
            qs = qs.filter(tracks__genre_id=genre_id).distinct()

        qs = qs.annotate(

            plays_28=Coalesce(
                Sum('tracks__play_count',
                    filter=Q(tracks__release_date__gte=d28)), 0),

            plays_7=Coalesce(
                Sum('tracks__play_count',
                    filter=Q(tracks__release_date__gte=d7)), 0),

            plays_prev_7=Coalesce(
                Sum(
                    'tracks__play_count',
                    filter=Q(
                        tracks__release_date__gte=d14,
                        tracks__release_date__lt=d7
                    )
                ), 0),

            listen_time_28=Coalesce(
                Sum('tracks__total_listen_time',
                    filter=Q(tracks__release_date__gte=d28)), 0),

            uniq_28=Coalesce(
                Sum('tracks__unique_listeners',
                    filter=Q(tracks__release_date__gte=d28)), 0),

            recent_tracks=Coalesce(
                Count('tracks',
                      filter=Q(tracks__release_date__gte=d14)), 0),

            shorts_views=Coalesce(
                Sum('tracks__short_videos__views'), 0),

            shorts_likes=Coalesce(
                Count('tracks__short_videos__likes', distinct=True), 0),

            shorts_shares=Coalesce(
                Sum('tracks__short_videos__shares_count'), 0),

            last_release=Max('tracks__release_date'),

        ).annotate(

            # ✅ FIXED (interval -> float days)
            days_since_release=ExpressionWrapper(
                Extract(now - F('last_release'), 'epoch') / Value(86400.0),
                output_field=FloatField()
            ),

            pop_28=ExpressionWrapper(
                Least(Value(1.0), (1.0 + F('plays_28')) / Value(1000.0)),
                output_field=FloatField()
            ),

            aud_28=ExpressionWrapper(
                Least(Value(1.0), (1.0 + F('uniq_28')) / Value(500.0)),
                output_field=FloatField()
            ),

            trend=ExpressionWrapper(
                F('plays_7') * 1.0 / (F('plays_28') + Value(1)),
                output_field=FloatField()
            ),

            growth=ExpressionWrapper(
                Case(
                    When(
                        plays_28__gt=0,
                        then=F('plays_7') * 1.0 / (F('plays_28') * 1.0)
                    ),
                    default=Value(0.0),
                    output_field=FloatField()
                ),
                output_field=FloatField()
            ),

            accel=ExpressionWrapper(
                (F('plays_7') - F('plays_prev_7')) /
                (F('plays_prev_7') + Value(1)),
                output_field=FloatField()
            ),

            virality=ExpressionWrapper(
                F('uniq_28') * 1.0 / (F('plays_28') + Value(1)),
                output_field=FloatField()
            ),

            fresh=ExpressionWrapper(
                Least(Value(1.0), F('recent_tracks') * Value(0.25)),
                output_field=FloatField()
            ),

            depth=ExpressionWrapper(
                Case(
                    When(
                        plays_28__gt=0,
                        then=F('listen_time_28') * 1.0 /
                        (F('plays_28') * Value(180.0))
                    ),
                    default=Value(0.0),
                    output_field=FloatField()
                ),
                output_field=FloatField()
            ),

            decay=ExpressionWrapper(
                Exp(Value(-0.1) * F('days_since_release')),
                output_field=FloatField()
            ),

            engagement=ExpressionWrapper(
                (
                    F('shorts_views') +
                    F('shorts_likes') * Value(3.0) +
                    F('shorts_shares') * Value(5.0)
                ) / Value(1000.0),
                output_field=FloatField()
            ),

        ).annotate(

            score=(
                0.25 * F('pop_28') +
                0.15 * F('aud_28') +
                0.18 * F('trend') +
                0.10 * F('growth') +
                0.08 * F('accel') +
                0.08 * F('virality') +
                0.07 * F('fresh') +
                0.04 * F('depth') +
                0.03 * F('engagement') +
                0.02 * F('decay')
            )

        ).annotate(

            trust=Case(
                When(depth__lt=0.15, then=Value(0.6)),
                When(virality__lt=0.01, then=Value(0.7)),
                default=Value(1.0),
                output_field=FloatField()
            )

        ).annotate(

            final_score=F('score') * F('trust')

        ).order_by(
            '-final_score',
            '-plays_7',
            '-plays_28',
            '-recent_tracks'
        ).distinct()

        limit = int(self.request.query_params.get('limit', 20))
        return qs[:limit]



class ArtistDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    lookup_field = "artistname"






def stream_audio(request, file_path):

    path = os.path.join(settings.MEDIA_ROOT, file_path)

    if not os.path.exists(path):
        return HttpResponse(status=404)

    file_size = os.path.getsize(path)
    range_header = request.headers.get("Range", None)

    if not range_header:
        response = StreamingHttpResponse(
            open(path, "rb"),
            content_type="audio/mpeg"
        )
        response["Content-Length"] = str(file_size)
        return response

    range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)

    if not range_match:
        return HttpResponse(status=416)

    start = int(range_match.group(1))
    end = range_match.group(2)

    if end:
        end = int(end)
    else:
        end = file_size - 1

    length = end - start + 1

    file = open(path, "rb")
    file.seek(start)

    response = StreamingHttpResponse(
        file,
        status=206,
        content_type="audio/mpeg"
    )

    response["Content-Length"] = str(length)
    response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
    response["Accept-Ranges"] = "bytes"

    return response
