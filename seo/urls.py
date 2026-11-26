from django.urls import path

from .views import (
    ArtistSEOView,
    SongSEOView,
    SitemapSEOView
)


urlpatterns = [
    path(
        "artist/<str:artistname>/",
        ArtistSEOView.as_view(),
        name="artist-seo",
    ),

    path(
        "song/<uuid:unique_id>/",
        SongSEOView.as_view(),
        name="song-seo",
    ),
       path(
        "sitemap/",
        SitemapSEOView.as_view(),
        name="seo-sitemap",
    ),
]
