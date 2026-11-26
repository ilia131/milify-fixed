from django.db.models import (
    Q,
    Count,
)

from rest_framework import (
    generics,
    status,
)

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Songs,
    TrackArtist,
)
from .models import Playlist
from .admin_serializers import AdminPlaylistSerializer

from .admin_serializers import (
    AdminSongSerializer,
    AdminSongCreateSerializer,
    AdminSongUpdateSerializer,
)

from .admin_pagination import (
    AdminSongPagination, AdminPlaylistPagination
)


from django.db.models import Count, Q

 





class AdminPlaylistListView(generics.ListAPIView):
    """
    Admin:
    List all user playlists
    """

    serializer_class = AdminPlaylistSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminPlaylistPagination

    def get_queryset(self):
        queryset = (
            Playlist.objects
            .select_related("user")
            .prefetch_related(
                "playlisttrack_set__song__artist"
            )
            .annotate(
                tracks_count=Count(
                    "playlisttrack",
                    distinct=True
                )
            )
            .order_by("-id")
        )

        search = self.request.query_params.get("search")

        if search:
            search = search.strip()

            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(user__username__icontains=search)
                | Q(user__email__icontains=search)
            )

        return queryset


class AdminPlaylistDetailView(generics.RetrieveDestroyAPIView):
    """
    Admin:
    View playlist details
    Delete playlist
    """

    serializer_class = AdminPlaylistSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "unique_id"

    queryset = (
        Playlist.objects
        .select_related("user")
        .prefetch_related(
            "playlisttrack_set__song__artist"
        )
        .annotate(
            tracks_count=Count(
                "playlisttrack",
                distinct=True
            )
        )
    )
class AdminSongListView(
    generics.ListAPIView
):

    serializer_class = AdminSongSerializer

    permission_classes = [
        IsAdminUser
    ]

    pagination_class = AdminSongPagination

    def get_queryset(self):

        queryset = (
            Songs.objects

            .select_related(
                "genre",
                "album",
            )

            .prefetch_related(
                "trackartist_set__artist"
            )

            .order_by(
                "-release_date"
            )
        )

        search = self.request.query_params.get(
            "search"
        )

        if search:

            queryset = queryset.filter(
                Q(title__icontains=search)

                | Q(
                    trackartist__artist__artistname__icontains=search
                )

                | Q(
                    genre__name__icontains=search
                )

                | Q(
                    album__title__icontains=search
                )
            ).distinct()

        genre = self.request.query_params.get(
            "genre"
        )

        if genre:
            queryset = queryset.filter(
                genre_id=genre
            )

        album = self.request.query_params.get(
            "album"
        )

        if album:
            queryset = queryset.filter(
                album_id=album
            )

        is_published = (
            self.request.query_params.get(
                "is_published"
            )
        )

        if is_published in [
            "true",
            "false"
        ]:

            queryset = queryset.filter(
                is_published=(
                    is_published == "true"
                )
            )

        verified = self.request.query_params.get(
            "verified"
        )

        if verified in [
            "true",
            "false"
        ]:

            queryset = queryset.filter(
                verified=(
                    verified == "true"
                )
            )

        artist = self.request.query_params.get(
            "artist"
        )

        if artist:

            queryset = queryset.filter(
                trackartist__artist_id=artist
            ).distinct()

        return queryset
    
    

class AdminSongDetailView(
    generics.RetrieveAPIView
):

    serializer_class = AdminSongSerializer

    permission_classes = [
        IsAdminUser
    ]

    lookup_field = "id"

    queryset = (
        Songs.objects

        .select_related(
            "genre",
            "album",
        )

        .prefetch_related(
            "trackartist_set__artist",
            "listens",
        )
    )
    

from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)


class AdminSongCreateView(
    generics.CreateAPIView
):

    permission_classes = [
        IsAdminUser
    ]

    serializer_class = (
        AdminSongCreateSerializer
    )

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]
    

class AdminSongUpdateView(
    generics.UpdateAPIView
):

    permission_classes = [
        IsAdminUser
    ]

    serializer_class = (
        AdminSongUpdateSerializer
    )

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    lookup_field = "id"

    queryset = Songs.objects.all()
    


class AdminSongTogglePublishedView(
    APIView
):

    permission_classes = [
        IsAdminUser
    ]

    def patch(self, request, id):

        try:
            song = Songs.objects.get(
                id=id
            )

        except Songs.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Song not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        song.is_published = (
            not song.is_published
        )

        song.save(
            update_fields=[
                "is_published"
            ]
        )

        return Response({
            "id": song.id,
            "title": song.title,
            "is_published": song.is_published,
        })
        

class AdminSongToggleVerifiedView(
    APIView
):

    permission_classes = [
        IsAdminUser
    ]

    def patch(self, request, id):

        try:
            song = Songs.objects.get(
                id=id
            )

        except Songs.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Song not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        song.verified = (
            not song.verified
        )

        song.save(
            update_fields=[
                "verified"
            ]
        )

        return Response({
            "id": song.id,
            "title": song.title,
            "verified": song.verified,
        })