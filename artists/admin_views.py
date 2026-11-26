# artists/admin_views.py

from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser
from .serializers import FollowArtist
from django.shortcuts import get_object_or_404
from artists.models import Artist
from artists.admin_serializers import (
    AdminArtistSerializer,
    AdminArtistCreateSerializer,
    AdminArtistUpdateSerializer,
    AdminFollowArtistSerializer,
)
from artists.admin_pagination import AdminArtistPagination , AdminFollowPagination

class AdminArtistListView(generics.ListAPIView):

    serializer_class = AdminArtistSerializer

    permission_classes = [
        IsAdminUser
    ]

    pagination_class = AdminArtistPagination

    def get_queryset(self):

        queryset = (
            Artist.objects
            .select_related("user")
            .annotate(
                followers_count=Count(
                    "followers",
                    distinct=True
                )
            )
            .order_by("-created_at")
        )

        search = self.request.query_params.get("search")

        if search:

            queryset = queryset.filter(
                Q(artistname__icontains=search)
                |
                Q(user__username__icontains=search)
                |
                Q(user__email__icontains=search)
            )

        is_featured = self.request.query_params.get(
            "is_featured"
        )

        if is_featured in ["true", "false"]:

            queryset = queryset.filter(
                is_featured=is_featured == "true"
            )

        is_active = self.request.query_params.get(
            "is_active"
        )

        if is_active in ["true", "false"]:

            queryset = queryset.filter(
                user__is_active=is_active == "true"
            )

        return queryset
    
class AdminArtistToggleFeaturedView(APIView):

    permission_classes = [
        IsAdminUser
    ]

    def patch(self, request, id):

        try:

            artist = Artist.objects.get(
                id=id
            )

        except Artist.DoesNotExist:

            return Response(
                {
                    "detail": "Artist not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        artist.is_featured = not artist.is_featured

        artist.save(
            update_fields=[
                "is_featured"
            ]
        )

        return Response({
            "id": artist.id,
            "artistname": artist.artistname,
            "is_featured": artist.is_featured
        })
    
class AdminArtistDetailView(
    generics.RetrieveAPIView
):

    serializer_class = AdminArtistSerializer

    permission_classes = [
        IsAdminUser
    ]

    queryset = (
        Artist.objects
        .select_related("user")
        .annotate(
            followers_count=Count(
                "followers",
                distinct=True
            )
        )
    )

    lookup_field = "id"
    

class AdminArtistToggleActiveView(APIView):

    permission_classes = [
        IsAdminUser
    ]

    def patch(self, request, id):

        try:

            artist = Artist.objects.select_related(
                "user"
            ).get(id=id)

        except Artist.DoesNotExist:

            return Response(
                {
                    "detail": "Artist not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        user = artist.user

        user.is_active = not user.is_active

        user.save(
            update_fields=[
                "is_active"
            ]
        )

        return Response({
            "id": artist.id,
            "artistname": artist.artistname,
            "is_active": user.is_active
        })
        


        

class AdminFollowListView(generics.ListAPIView):

    serializer_class = AdminFollowArtistSerializer
    permission_classes = [IsAdminUser]

    pagination_class = AdminFollowPagination

    def get_queryset(self):

        queryset = (
            FollowArtist.objects
            .select_related(
                "user",
                "artist",
            )
            .order_by("-created_at")
        )

        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search)
                |
                Q(user__email__icontains=search)
                |
                Q(artist__artistname__icontains=search)
            )

        artist_id = self.request.query_params.get("artist")

        if artist_id:
            queryset = queryset.filter(
                artist_id=artist_id
            )

        return queryset
    
    
    
class AdminArtistCreateView(
    generics.CreateAPIView
):

    permission_classes = [
        IsAdminUser
    ]

    serializer_class = AdminArtistCreateSerializer

    def perform_create(self, serializer):

        serializer.save()
        

class AdminArtistUpdateView(
    generics.UpdateAPIView
):

    permission_classes = [
        IsAdminUser
    ]

    queryset = Artist.objects.select_related(
        "user"
    )

    serializer_class = AdminArtistUpdateSerializer

    lookup_field = "id"

    def get_object(self):

        return get_object_or_404(
            self.queryset,
            id=self.kwargs["id"]
        )