from accounts.models import UserNotification, PushSubscription 
from rest_framework import serializers



class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "url",
            "created_at",
            
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = [
            "id",
            "endpoint",
            "p256dh",
            "auth",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def create(self, validated_data):
        user = self.context["request"].user

        subscription, created = PushSubscription.objects.update_or_create(
            endpoint=validated_data["endpoint"],
            defaults={
                "user": user,
                "p256dh": validated_data["p256dh"],
                "auth": validated_data["auth"],
            },
        )

        return subscription