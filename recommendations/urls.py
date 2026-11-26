from django.urls import path
from .views import   Track2VecRecommendView , ForYouHybridView , FreshTracksView

urlpatterns = [
     path("suggest/<uuid:song_uuid>/", Track2VecRecommendView.as_view(), name="track2vec"),
    path("for-you/", ForYouHybridView.as_view(), name="for-you"),
     path("fresh/",FreshTracksView.as_view(),name="recommend-fresh"),
]