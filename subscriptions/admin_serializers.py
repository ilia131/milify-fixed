from rest_framework import serializers

from .models import (
    Payment,
    Subscription,
)


class AdminPaymentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    subscription_type = serializers.SerializerMethodField()
    subscription_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment

        fields = [
            "id",
            "username",
            "user_email",
            "amount",
            "status",
            "authority",
            "ref_id",
            "subscription_type",
            "subscription_name",
            "created_at",
            "paid_at",
        ]

    def get_subscription_type(self, obj):
        if obj.subscription_id:
            return "PLATFORM"

        if obj.artist_subscription_id:
            return "ARTIST"

        return None

    def get_subscription_name(self, obj):
        if obj.subscription_id:
            return obj.subscription.plan.name

        if obj.artist_subscription_id:
            return obj.artist_subscription.plan.name

        return None


class AdminSubscriptionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    plan_name = serializers.CharField(
        source="plan.name",
        read_only=True,
    )

    plan_price = serializers.DecimalField(
        source="plan.price",
        max_digits=12,
        decimal_places=0,
        read_only=True,
    )

    is_currently_active = serializers.BooleanField(
        source="is_active_subscription",
        read_only=True,
    )

    class Meta:
        model = Subscription

        fields = [
            "id",
            "username",
            "user_email",
            "plan_name",
            "plan_price",
            "status",
            "started_at",
            "expires_at",
            "is_currently_active",
            "created_at",
            "updated_at",
        ]