from django.contrib import admin

from .models import (
    Beat,
    BeatLicense,
    BeatPurchase,
    ProducerProfile,
)


# =========================================================
# Producer Profile
# =========================================================

@admin.register(ProducerProfile)
class ProducerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "producer_name",
        "user",
        "is_verified",
        "is_active",
        "total_sales",
        "total_revenue",
        "created_at",
    )

    list_filter = (
        "is_verified",
        "is_active",
        "created_at",
    )

    search_fields = (
        "producer_name",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "uuid",
        "total_sales",
        "total_revenue",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25


# =========================================================
# Beat
# =========================================================

@admin.register(Beat)
class BeatAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "producer",
        "genre",
        "price",
        "is_active",
        "is_featured",
        "plays",
        "sales",
        "created_at",
    )

    list_filter = (
        "genre",
        "is_active",
        "is_featured",
        "created_at",
    )

    search_fields = (
        "title",
        "slug",
        "producer__producer_name",
    )

    readonly_fields = (
        "plays",
        "sales",
        "created_at",
        "updated_at",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    autocomplete_fields = (
        "producer",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25


# =========================================================
# Beat License
# =========================================================

@admin.register(BeatLicense)
class BeatLicenseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "beat",
        "license_type",
        "price",
        "commercial_use",
        "stems_included",
        "exclusive",
        "is_active",
        "created_at",
    )

    list_filter = (
        "license_type",
        "commercial_use",
        "stems_included",
        "exclusive",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "beat__title",
        "beat__producer__producer_name",
    )

    readonly_fields = (
        "created_at",
    )

    autocomplete_fields = (
        "beat",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25


# =========================================================
# Beat Purchase
# =========================================================

@admin.register(BeatPurchase)
class BeatPurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "beat",
        "license",
        "price",
        "platform_fee",
        "producer_revenue",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "id",
        "user__username",
        "user__email",
        "beat__title",
        "beat__producer__producer_name",
        "license__name",
    )

    readonly_fields = (
        "id",
        "user",
        "beat",
        "license",
        "price",
        "platform_fee",
        "producer_revenue",
        "created_at",
    )

    autocomplete_fields = ()

    ordering = (
        "-created_at",
    )

    list_per_page = 25