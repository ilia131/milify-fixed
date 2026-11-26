from django.urls import path

from .views import (
    BeatListView,
    BeatDetailView,
    ProducerProfileListView,
    ProducerProfileDetailView,
    ProducerBeatListView,
    BuyBeatView,
    MyBeatPurchasesView,
    DownloadBeatView,
    StreamPurchasedBeatView,
)


urlpatterns = [

    # ==========================================
    # BEATS
    # ==========================================

    path(
        "beats/",
        BeatListView.as_view(),
        name="beat-list",
    ),

    path(
        "beats/<int:id>/",
        BeatDetailView.as_view(),
        name="beat-detail",
    ),

    path(
        "beats/<int:beat_id>/buy/",
        BuyBeatView.as_view(),
        name="buy-beat",
    ),


    # ==========================================
    # PRODUCERS
    # ==========================================

    path(
        "producers/",
        ProducerProfileListView.as_view(),
        name="producer-list",
    ),

    path(
        "producers/<uuid:uuid>/",
        ProducerProfileDetailView.as_view(),
        name="producer-detail",
    ),

    path(
        "producers/<uuid:uuid>/beats/",
        ProducerBeatListView.as_view(),
        name="producer-beats",
    ),


    # ==========================================
    # USER PURCHASES
    # ==========================================

    path(
        "my/purchases/",
        MyBeatPurchasesView.as_view(),
        name="my-beat-purchases",
    ),
    path(
    "purchases/<uuid:purchase_id>/download/",
    DownloadBeatView.as_view(),
    name="download-beat",
    
),
    path(
    "purchases/<uuid:purchase_id>/stream/",
    StreamPurchasedBeatView.as_view(),
    name="stream-purchased-beat",
),
]