from django.contrib import admin

from .models import (
    Advertiser,
    Campaign,
    Advertisement,
    AdImpression,
    AdClick,
)


@admin.register(Advertiser)
class AdvertiserAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "website",
        "is_active",
        "created_at",
    ]

    search_fields = [
        "name",
    ]

    list_filter = [
        "is_active",
    ]


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "advertiser",
        "budget",
        "spent",
        "status",
        "start_at",
        "end_at",
    ]

    search_fields = [
        "name",
        "advertiser__name",
    ]

    list_filter = [
        "status",
    ]


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):

    list_display = [
        "title",
        "campaign",
        "ad_type",
        "placement",
        "pricing_model",
        "price",
        "is_active",
    ]

    search_fields = [
        "title",
        "campaign__name",
        "campaign__advertiser__name",
    ]

    list_filter = [
        "ad_type",
        "placement",
        "pricing_model",
        "is_active",
    ]


@admin.register(AdImpression)
class AdImpressionAdmin(admin.ModelAdmin):

    list_display = [
        "ad",
        "user",
        "watched_seconds",
        "watched_percentage",
        "completed",
        "created_at",
    ]

    list_filter = [
        "completed",
    ]


@admin.register(AdClick)
class AdClickAdmin(admin.ModelAdmin):

    list_display = [
        "ad",
        "user",
        "created_at",
    ]