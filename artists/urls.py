from django.urls import path
from .views import ArtistListView, ArtistDetailView , stream_audio , UserFavoriteArtistsView ,   ArtistCreateAPIView, ArtistUpdateAPIView , ArtistUpdateAPIView2 , ArtistDashboardView , ArtistFollowerChart
from . import views
from artists.admin_views import (
    AdminArtistListView,
    AdminArtistDetailView,
    AdminArtistToggleFeaturedView,
    AdminArtistToggleActiveView,
    AdminFollowListView,
    AdminArtistCreateView,
    AdminArtistUpdateView
)
urlpatterns = [
     path(
        "admin/artists/",
        AdminArtistListView.as_view(),
        name="admin-artists",
    ),

    path(
        "admin/artists/<int:id>/",
        AdminArtistDetailView.as_view(),
        name="admin-artist-detail",
    ),

    path(
        "admin/artists/<int:id>/toggle-featured/",
        AdminArtistToggleFeaturedView.as_view(),
        name="admin-artist-toggle-featured",
    ),

    path(
        "admin/artists/<int:id>/toggle-active/",
        AdminArtistToggleActiveView.as_view(),
        name="admin-artist-toggle-active",
    ),

    path(
        "admin/follows/",
        AdminFollowListView.as_view(),
        name="admin-follows",
    ),
    path(
    "admin/artists/create/",
    AdminArtistCreateView.as_view(),
    name="admin-artist-create",
),

path(
    "admin/artists/<int:id>/update/",
    AdminArtistUpdateView.as_view(),
    name="admin-artist-update",
),
    #USERVIEW
    path(
        "artists/<str:artistname>/songs/",
        views.ArtistSongsView.as_view()
    ),
    path(
        "artists2/",
        ArtistCreateAPIView.as_view(),
        name="artist-create"
    ),
    path(
        "artists/<int:pk>/",
        ArtistUpdateAPIView.as_view(),
        name="artist-update"
    ),
    #Artist_PanelAdmin
    path(
        "dashboard/<str:artistname>/",
        ArtistDashboardView.as_view(),
        name="artist-dashboard",
    ),

    path(
        "dashboard/<str:artistname>/followers-chart/",
        ArtistFollowerChart.as_view(),
        name="artist-followers-chart",
    ),
    #####
    path(
    "artists2/<str:artistname>/",
    ArtistUpdateAPIView2.as_view(),
    name="artist-update",
),
    path(
        "artists/<str:artistname>/albums/",
        views.ArtistAlbumsView.as_view()
    ),
    path("artists/<uuid:artist_uuid>/follow/", views.toggle_follow_artist),

    path("artists/following/", views.user_following_artists),

    path("artists/<uuid:artist_uuid>/followers/", views.artist_followers),
  
    path("artists/<uuid:artist_uuid>/is-following/", views.is_following),
    #ARTIST
    path("artists/", ArtistListView.as_view(), name="artists"),
    path("artistslist/", ArtistListView.as_view(), name="artist-list"),
    path("me/favorite-artists/", UserFavoriteArtistsView.as_view(), name="current-user-favorite-artists"),
    path("artists/<str:artistname>/", ArtistDetailView.as_view(), name="artist-detail"),
    path("stream/<path:file_path>/", stream_audio),
]
