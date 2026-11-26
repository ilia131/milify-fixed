from django.urls import path

from .views import (
    SubscriptionPlanListView,
    MySubscriptionView,
    PurchaseSubscriptionView,
)

from .views import (
    ArtistSubscriptionPlanView,
    ArtistSubscriptionTrackCreateView,
    ArtistSubscriptionTrackApprovalView,
    ArtistSubscriptionTrackStatusView,
    ArtistSubscriptionPurchaseView,
    MyArtistSubscriptionsView,
    SongSubscriptionAccessView,
)
from .admin_views import (
    AdminPaymentListView,
    AdminSubscriptionListView,
    AdminRevenueView,
    AdminRevenueChartView,
)



urlpatterns = [
    
      path(
        "access/payments/",
        AdminPaymentListView.as_view(),
        name="admin-payments",
    ),

    path(
        "access/subscriptions/",
        AdminSubscriptionListView.as_view(),
        name="admin-subscriptions",
    ),

    path(
        "access/revenue/",
        AdminRevenueView.as_view(),
        name="admin-revenue",
    ),

    path(
        "access/revenue/chart/",
        AdminRevenueChartView.as_view(),
        name="admin-revenue-chart",
    ),
    #user
  path(
    "artists/<str:artistname>/subscription/",
    ArtistSubscriptionPlanView.as_view(),
    name="artist-subscription-plan",
),

path(
    "artists/subscription/tracks/<uuid:song_id>/",
    ArtistSubscriptionTrackCreateView.as_view(),
    name="artist-subscription-track-create",
),

path(
    "artists/subscription/tracks/<uuid:song_id>/approval/",
    ArtistSubscriptionTrackApprovalView.as_view(),
    name="artist-subscription-track-approval",
),

path(
    "artists/subscription/tracks/<uuid:song_id>/status/",
    ArtistSubscriptionTrackStatusView.as_view(),
    name="artist-subscription-track-status",
),

path(
    "artists/<str:artistname>/subscription/purchase/",
    ArtistSubscriptionPurchaseView.as_view(),
    name="artist-subscription-purchase",
),

    # -----------------------------------------
    # My subscriptions
    # -----------------------------------------

    path(
        "me/artist-subscriptions/",
        MyArtistSubscriptionsView.as_view(),
        name="my-artist-subscriptions",
    ),

    # -----------------------------------------
    # Song access
    # -----------------------------------------

    path(
        "songs/<uuid:song_id>/subscription/access/",
        SongSubscriptionAccessView.as_view(),
        name="song-subscription-access",
    ),
    path(
        "plans/",
        SubscriptionPlanListView.as_view(),
        name="subscription-plans",
    ),

    path(
        "me/",
        MySubscriptionView.as_view(),
        name="my-subscription",
    ),

    path(
        "purchase/",
        PurchaseSubscriptionView.as_view(),
        name="purchase-subscription",
    ),
]