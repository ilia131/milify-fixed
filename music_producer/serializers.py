from rest_framework import serializers

from .models import (
    ProducerProfile,
    Beat,
    BeatLicense,
    BeatPurchase,
)


class ProducerUserSerializer(serializers.ModelSerializer):
    """
    اطلاعات عمومی UserListener مربوط به Producer
    """

    class Meta:
        model = ProducerProfile._meta.get_field("user").remote_field.model

        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
        ]


class ProducerProfileSerializer(serializers.ModelSerializer):

    user = ProducerUserSerializer(
        read_only=True
    )

    class Meta:
        model = ProducerProfile

        fields = [
            "id",
            "uuid",
            "producer_name",
            "bio",
            "profile_pic",
            "cover_image",
            "instagram",
            "youtube",
            "is_verified",
            "is_active",
            "total_sales",
            "total_revenue",
            "user",
            "created_at",
        ]


class BeatLicenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = BeatLicense

        fields = [
            "id",
            "license_type",
            "name",
            "price",
            "commercial_use",
            "stems_included",
            "exclusive",
            "is_active",
        ]


class BeatSerializer(serializers.ModelSerializer):

    producer = ProducerProfileSerializer(
        read_only=True
    )

    licenses = BeatLicenseSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Beat

        fields = [
            "id",
            "title",
            "slug",
            "genre",
            "bpm",
            "key",
            "cover",
            "preview_audio",
            "description",
            "price",
            "is_active",
            "is_featured",
            "plays",
            "sales",
            "producer",
            "licenses",
            "created_at",
            "updated_at",
        ]


class BeatListSerializer(serializers.ModelSerializer):

    producer = ProducerProfileSerializer(
        read_only=True
    )

    class Meta:
        model = Beat

        fields = [
            "id",
            "title",
            "slug",
            "genre",
            "bpm",
            "key",
            "cover",
            "preview_audio",
            "price",
            "is_featured",
            "plays",
            "sales",
            "producer",
            "created_at",
        ]


class BeatPurchaseSerializer(serializers.ModelSerializer):

    beat = BeatSerializer(
        read_only=True
    )

    class Meta:
        model = BeatPurchase

        fields = [
            "id",
            "beat",
            "price",
            "status",
            "created_at",
        ]