from rest_framework import serializers

from .models import UserListener
from subscriptions.models import (
    Subscription,
    ArtistSubscription,
    Wallet,
)

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import UserListener , SupportRequest



class SupportRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupportRequest

        fields = [
            "id",
            "email",
            "subject",
            "message",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_email(self, value):
        return value.strip().lower()

    def validate_subject(self, value):
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "موضوع باید حداقل ۳ کاراکتر باشد."
            )

        return value

    def validate_message(self, value):
        value = value.strip()

        if len(value) < 10:
            raise serializers.ValidationError(
                "متن پیام باید حداقل ۱۰ کاراکتر باشد."
            )

        if len(value) > 5000:
            raise serializers.ValidationError(
                "متن پیام نمی‌تواند بیشتر از ۵۰۰۰ کاراکتر باشد."
            )

        return value

class ChangePasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        trim_whitespace=False,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
    )

    def validate_current_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "رمز عبور فعلی اشتباه است."
            )

        return value

    def validate(self, attrs):

        new_password = attrs["new_password"]
        confirm_password = attrs["confirm_password"]

        if new_password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "تکرار رمز عبور با رمز جدید مطابقت ندارد."
            })

        user = self.context["request"].user

        if user.check_password(new_password):
            raise serializers.ValidationError({
                "new_password": "رمز جدید نمی‌تواند با رمز فعلی یکسان باشد."
            })

        return attrs

    def save(self, **kwargs):

        user = self.context["request"].user

        user.set_password(
            self.validated_data["new_password"]
        )

        user.save(
            update_fields=["password"]
        )

        return user



class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(
        source="plan.name",
        read_only=True
    )

    plan_price = serializers.DecimalField(
        source="plan.price",
        max_digits=12,
        decimal_places=0,
        read_only=True
    )

    is_active_subscription = serializers.BooleanField(
        read_only=True
    )

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan_name",
            "plan_price",
            "status",
            "started_at",
            "expires_at",
            "is_active_subscription",
            "created_at",
        ]


class ArtistSubscriptionSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(
        source="artist.artistname",
        read_only=True
    )

    artist_id = serializers.UUIDField(
        source="artist.uuid",
        read_only=True
    )

    plan_name = serializers.CharField(
        source="plan.name",
        read_only=True
    )

    plan_price = serializers.DecimalField(
        source="plan.price",
        max_digits=12,
        decimal_places=0,
        read_only=True
    )

    is_active_subscription = serializers.BooleanField(
        read_only=True
    )

    class Meta:
        model = ArtistSubscription

        fields = [
            "id",
            "artist_id",
            "artist_name",
            "plan_name",
            "plan_price",
            "status",
            "started_at",
            "expires_at",
            "is_active_subscription",
            "created_at",
        ]


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet

        fields = [
            "id",
            "balance",
            "created_at",
            "updated_at",
        ]


class UserProfileSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()

    has_active_subscription = serializers.BooleanField(
        read_only=True
    )

    subscriptions = UserSubscriptionSerializer(
        many=True,
        read_only=True
    )

    artist_subscriptions = ArtistSubscriptionSerializer(
        many=True,
        read_only=True
    )

    wallet = WalletSerializer(
        read_only=True
    )

    class Meta:
        model = UserListener

        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "profile_pic",
            "image_url",
            "is_artist",
            "favorite_genres",
            "favorite_artists",
            "has_active_subscription",
            "wallet",
            "is_staff",
            "subscriptions",
            "artist_subscriptions",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "email",
            "image_url",
            "is_artist",
            "is_staff"
            "has_active_subscription",
            "wallet",
            "subscriptions",
            "artist_subscriptions",
            "created_at",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")

        if not obj.profile_pic:
            return None

        if request:
            return request.build_absolute_uri(
                obj.profile_pic.url
            )

        return obj.profile_pic.url

    def validate_username(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "نام کاربری نمی‌تواند خالی باشد."
            )

        queryset = UserListener.objects.filter(
            username__iexact=value
        ).exclude(
            pk=self.instance.pk
        )

        if queryset.exists():
            raise serializers.ValidationError(
                "این نام کاربری قبلاً استفاده شده است."
            )

        return value

    def validate_first_name(self, value):
        return value.strip()

    def validate_last_name(self, value):
        return value.strip()
