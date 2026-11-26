from django.urls import path , include
from .views import SongPlayerView, SongListenView
from .views import ( fresh_tracks , trending_tracks_view, trending_tracks ,
PopularAlbumsView   , AlbumSearchView , ExploreShortVideoView ,
ShortVideoDetailView , ArtistAlbumCreateView , ArtistSongCreateView , ArtistShortCreateView , ArtistAlbumListView ,
ArtistShortListView ,ArtistSongListView , ArtistAlbumsView , BigCardArtistView , AlbumTracksView , ToggleLikeSong,
LikedSongsList , LikedStatusView , GlobalSearchView , BrowseGenresView , SongDetailView , AlbumListView , ArtistSongCreate2View,
SongSkipView
)
from .admin_views import (
    AdminSongListView,
    AdminSongDetailView,
    AdminSongCreateView,
    AdminSongUpdateView,
    AdminSongTogglePublishedView,
    AdminSongToggleVerifiedView,

)
from rest_framework.routers import DefaultRouter
from .views import PlaylistViewSet
from .admin_views import (
    AdminPlaylistListView,
    AdminPlaylistDetailView,
)
from .views import (
    ShortVideoLikeView,
    ShortVideoCommentsView,
    ShortVideoCommentDeleteView,
    ShortVideoCommentLikeView,
    ShortVideoShareView,
)
from .recommendation_views import CategoryRecommendationsView ,RecommendationView
router = DefaultRouter()
router.register(r'playlists', PlaylistViewSet, basename='playlist')


urlpatterns = [
        path(
        "short-videos/<uuid:uuid>/like/",
        ShortVideoLikeView.as_view(),
        name="short-video-like",
    ),

    path(
        "short-videos/<uuid:uuid>/comments/",
        ShortVideoCommentsView.as_view(),
        name="short-video-comments",
    ),

    path(
        "short-video-comments/<int:comment_id>/",
        ShortVideoCommentDeleteView.as_view(),
        name="short-video-comment-delete",
    ),

    path(
        "short-video-comments/<int:comment_id>/like/",
        ShortVideoCommentLikeView.as_view(),
        name="short-video-comment-like",
    ),

    path(
        "short-videos/<uuid:uuid>/share/",
        ShortVideoShareView.as_view(),
        name="short-video-share",
    ),
      path(
        "access/songs/",
        AdminSongListView.as_view(),
        name="admin-song-list",
    ),

    path(
        "access/songs/<int:id>/",
        AdminSongDetailView.as_view(),
        name="admin-song-detail",
    ),

    path(
        "access/songs/create/",
        AdminSongCreateView.as_view(),
        name="admin-song-create",
    ),
    path(
    "access/playlists/",
    AdminPlaylistListView.as_view(),
    name="admin-playlist-list"
),

path(
    "access/playlists/<uuid:unique_id>/",
    AdminPlaylistDetailView.as_view(),
    name="admin-playlist-detail"
),

    path(
        "access/songs/<int:id>/update/",
        AdminSongUpdateView.as_view(),
        name="admin-song-update",
    ),

    path(
        "access/songs/<int:id>/toggle-published/",
        AdminSongTogglePublishedView.as_view(),
        name="admin-song-toggle-published",
    ),

    path(
        "access/songs/<int:id>/toggle-verified/",
        AdminSongToggleVerifiedView.as_view(),
        name="admin-song-toggle-verified",
    ),
    #user
    path('', include(router.urls)),
    path(
        "tracks/<str:unique_id>/",
        SongDetailView.as_view(),
        
        name="song-detail",
    ),
    
    path("search/", GlobalSearchView.as_view()),
    path("genres/browse/", BrowseGenresView.as_view(), name="browse-genres"),
    path("genres/browse/<str:name>/", BrowseGenresView.as_view()),

    path("big-card-artists/", BigCardArtistView.as_view(), name="big-card-artists"),
    path(
        "album/<str:artist_name>/<str:album_title>/",
        AlbumTracksView.as_view(),
        name="album-tracks"
    ),
    #Liked_Song
    path("songs/<uuid:song_id>/like/", ToggleLikeSong.as_view()),
    path("liked-songs/", LikedSongsList.as_view()),
    path("songs/liked/status/", LikedStatusView.as_view()),

    path("player/<uuid:unique_id>/", SongPlayerView.as_view(), name="song-player"),
    path("player/<uuid:unique_id>/listen/", SongListenView.as_view(), name="song-listen"),
    path("fresh-tracks/", fresh_tracks),
    path("trending/", trending_tracks),
    path('albums/popular/', PopularAlbumsView.as_view(), name='popular_albums'),
    path("albums/popular/detail/", AlbumSearchView.as_view()),
    path("albums/", AlbumListView.as_view()),
    path("shorts/explore/", ExploreShortVideoView.as_view(), name="shorts-explore"),
    path("shorts/<uuid:uuid>/", ShortVideoDetailView.as_view(), name="short-detail"),
    #AGent_System
    path("artist2/songs/create/", ArtistSongCreate2View.as_view()),

    #ADMIN PANEL
    path("artist/albums/create/", ArtistAlbumCreateView.as_view()),
    path("artist/albums/", ArtistAlbumListView.as_view()),

    path("artist/songs/", ArtistSongListView.as_view()),
    path("artist/songs/create/", ArtistSongCreateView.as_view()),

    path("artist/shorts/create/", ArtistShortCreateView.as_view()),
    path("artist/shorts/", ArtistShortListView.as_view()),
    path("my-albums/", ArtistAlbumsView.as_view(), name="artist-albums"),
    #ML
    path(
        "categories/",
        CategoryRecommendationsView.as_view(),
        name="category-recommendations",
    ),
    path(
    "songs/<str:unique_id>/skip/",
    SongSkipView.as_view(),
    name="song-skip",
),  
      path(
        "tt/recommendations/",
        RecommendationView.as_view(),
        name="recommendations",
    ),

    path(
        "tt/recommendations/categories/",
        CategoryRecommendationsView.as_view(),
        name="category-recommendations",
    ),
      


]
