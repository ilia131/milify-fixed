from rest_framework import serializers

from .models import (
    SubscriptionPlan,
    Subscription,
)


class SubscriptionPlanSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = SubscriptionPlan

        fields = [
            "id",
            "name",
            "description",
            "price",
            "duration_days",
        ]


class SubscriptionSerializer(
    serializers.ModelSerializer
):

    plan = SubscriptionPlanSerializer(
        read_only=True
    )

    is_active = serializers.BooleanField(
        source="is_active_subscription",
        read_only=True
    )

    class Meta:
        model = Subscription

        fields = [
            "id",
            "plan",
            "status",
            "started_at",
            "expires_at",
            "is_active",
            "created_at",
        ]