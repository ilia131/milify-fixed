from django.contrib import admin

from .models import (
    Wallet,
    WalletTransaction,
    SubscriptionPlan,
    Subscription,
    Payment,
    ArtistSubscriptionPlan,
    ArtistSubscription,
    ArtistSubscriptionTrack,
)


# =========================================================
# Wallet
# =========================================================

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "balance",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# Wallet Transactions
# =========================================================

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "wallet",
        "amount",
        "transaction_type",
        "description",
        "created_at",
    )

    list_filter = (
        "transaction_type",
        "created_at",
    )

    search_fields = (
        "wallet__user__username",
        "wallet__user__email",
        "description",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# Generic Subscription Plans
# =========================================================

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "duration_days",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "duration_days",
    )

    search_fields = (
        "name",
        "description",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# Generic Subscriptions
# =========================================================

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "status",
        "started_at",
        "expires_at",
        "created_at",
    )

    list_filter = (
        "status",
        "plan",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "plan__name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# Payments
# =========================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount",
        "status",
        "subscription",
        "artist_subscription",
        "authority",
        "ref_id",
        "created_at",
        "paid_at",
    )

    list_filter = (
        "status",
        "created_at",
        "paid_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "authority",
        "ref_id",
    )

    readonly_fields = (
        "id",
        "created_at",
        "paid_at",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# Artist Subscription Plans
# =========================================================

@admin.register(ArtistSubscriptionPlan)
class ArtistSubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "artist",
        "name",
        "price",
        "duration_days",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "duration_days",
        "created_at",
    )

    search_fields = (
        "artist__artistname",
        "name",
        "description",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# Artist Subscriptions
# =========================================================

@admin.register(ArtistSubscription)
class ArtistSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "artist",
        "plan",
        "status",
        "started_at",
        "expires_at",
        "created_at",
    )

    list_filter = (
        "status",
        "artist",
        "plan",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "artist__artistname",
        "plan__name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# Artist Subscription Tracks
# =========================================================

@admin.register(ArtistSubscriptionTrack)
class ArtistSubscriptionTrackAdmin(admin.ModelAdmin):
    list_display = (
        "song",
        "artist",
        "status",
        "approved_at",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "artist",
        "created_at",
        "approved_at",
    )

    search_fields = (
        "song__title",
        "artist__artistname",
    )

    readonly_fields = (
        "id",
        "approved_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )