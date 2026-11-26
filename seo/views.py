from django.shortcuts import get_object_or_404

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from artists.models import Artist
from music.models import Songs
from .models import ArtistSEO , SongSEO
from .serializers import ArtistSEOSerializer , SongSEOSerializer


class ArtistSEOView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, artistname):

        artist = get_object_or_404(
                Artist.objects.select_related("user"),
                artistname=artistname,
            )

        seo, created = ArtistSEO.objects.get_or_create(
            artist=artist
        )

        serializer = ArtistSEOSerializer(
            seo,
            context={
                "request": request,
            },
        )

        return Response(serializer.data)
    
    
    




class SongSEOView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, unique_id):

        song = get_object_or_404(
            Songs.objects.prefetch_related(
                "trackartist_set__artist"
            ),
            unique_id=unique_id,
        )

        seo, created = SongSEO.objects.get_or_create(
            song=song
        )

        serializer = SongSEOSerializer(
            seo,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data
        )
        
        
        

class SitemapSEOView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        artists = Artist.objects.filter(
            # شرط public بودن Artist اگر داری
        ).values(
            "uuid",
            "artistname",
        )

        songs = Songs.objects.filter(
            is_published=True
        ).values(
            "unique_id",
            "release_date",
        )

        return Response({
            "artists": list(artists),
            "songs": list(songs),
        })
