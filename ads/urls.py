from django.urls import path

# =========================================================
# PUBLIC VIEWS
# =========================================================

from .views import (
    AdvertiserListCreateView,
    CampaignListCreateView,
    AdvertisementListCreateView,
    AdvertisementDetailView,
    AdImpressionView,
    AdClickView,
)


# =========================================================
# ADMIN VIEWS
# =========================================================

from .admin_views import (
    AdminAdvertisementListCreateView,
    AdminAdvertisementDetailView,
    AdminAdvertisementStatsView,
    
)


# =========================================================
# URL PATTERNS
# =========================================================

urlpatterns = [

    # =====================================================
    # ADMIN ADS
    # =====================================================

    # List + Create Advertisement
    # GET  /ads/access/ads/
    # POST /ads/access/ads/
    path(
        "access/ads/",
        AdminAdvertisementListCreateView.as_view(),
        name="admin-ads",
    ),

    # Detail + Update + Delete Advertisement
    # GET    /ads/access/ads/<id>/
    # PUT    /ads/access/ads/<id>/
    # PATCH  /ads/access/ads/<id>/
    # DELETE /ads/access/ads/<id>/
    path(
        "access/ads/<uuid:id>/",
        AdminAdvertisementDetailView.as_view(),
        name="admin-ad-detail",
    ),

    # Advertisement Statistics
    # GET /ads/access/ads/<id>/stats/
    path(
        "access/ads/<uuid:id>/stats/",
        AdminAdvertisementStatsView.as_view(),
        name="admin-ad-stats",
    ),


    # =====================================================
    # PUBLIC ADVERTISERS
    # =====================================================

    # GET  /ads/advertisers/
    # POST /ads/advertisers/
    path(
        "advertisers/",
        AdvertiserListCreateView.as_view(),
        name="advertiser-list-create",
    ),


    # =====================================================
    # PUBLIC CAMPAIGNS
    # =====================================================

    # GET  /ads/campaigns/
    # POST /ads/campaigns/
    path(
        "campaigns/",
        CampaignListCreateView.as_view(),
        name="campaign-list-create",
    ),


    # =====================================================
    # PUBLIC ADVERTISEMENTS
    # =====================================================

    # GET  /ads/advertisements/
    # POST /ads/advertisements/
    path(
        "advertisements/",
        AdvertisementListCreateView.as_view(),
        name="advertisement-list-create",
    ),


    # =====================================================
    # PUBLIC ADVERTISEMENT DETAIL
    # =====================================================

    # GET /ads/advertisements/<id>/
    path(
        "advertisements/<uuid:pk>/",
        AdvertisementDetailView.as_view(),
        name="advertisement-detail",
    ),


    # =====================================================
    # AD IMPRESSION
    # =====================================================

    # POST /ads/advertisements/<id>/impression/
    path(
        "advertisements/<uuid:ad_id>/impression/",
        AdImpressionView.as_view(),
        name="ad-impression",
    ),


    # =====================================================
    # AD CLICK
    # =====================================================

    # POST /ads/advertisements/<id>/click/
    path(
        "advertisements/<uuid:ad_id>/click/",
        AdClickView.as_view(),
        name="ad-click",
    ),
]