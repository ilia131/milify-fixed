from rest_framework import serializers

from .models import (
    Advertiser,
    Campaign,
    Advertisement,
)


class AdminAdvertisementListSerializer(
    serializers.ModelSerializer
):
    campaign_name = serializers.CharField(
        source="campaign.name",
        read_only=True,
    )

    advertiser_name = serializers.CharField(
        source="campaign.advertiser.name",
        read_only=True,
    )

    budget = serializers.DecimalField(
        source="campaign.budget",
        max_digits=20,
        decimal_places=2,
        read_only=True,
    )

    spent = serializers.DecimalField(
        source="campaign.spent",
        max_digits=20,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Advertisement

        fields = [
            "id",
            "title",
            "description",
            "ad_type",
            "image",
            "video",
            "target_url",
            "placement",
            "pricing_model",
            "price",
            "duration",
            "is_active",

            "campaign",
            "campaign_name",
            "advertiser_name",
            "budget",
            "spent",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class AdminAdvertisementCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Advertisement

        fields = [
            "id",
            "campaign",
            "title",
            "description",
            "ad_type",
            "image",
            "video",
            "target_url",
            "placement",
            "pricing_model",
            "price",
            "duration",
            "is_active",
        ]

        read_only_fields = [
            "id",
        ]

    def validate(self, attrs):
        ad_type = attrs.get(
            "ad_type",
            getattr(
                self.instance,
                "ad_type",
                None,
            ),
        )

        image = attrs.get("image")

        video = attrs.get("video")

        if ad_type == "IMAGE":
            if not image and not self.instance:
                raise serializers.ValidationError({
                    "image": "برای تبلیغ تصویری، تصویر الزامی است."
                })

        if ad_type == "VIDEO":
            if not video and not self.instance:
                raise serializers.ValidationError({
                    "video": "برای تبلیغ ویدیویی، ویدیو الزامی است."
                })

        if ad_type == "IMAGE":
            if video:
                raise serializers.ValidationError({
                    "video": "تبلیغ IMAGE نباید ویدیو داشته باشد."
                })

        if ad_type == "VIDEO":
            if image:
                raise serializers.ValidationError({
                    "image": "تبلیغ VIDEO نباید تصویر داشته باشد."
                })

        return attrs


class AdminAdvertisementDetailSerializer(
    serializers.ModelSerializer
):
    campaign_name = serializers.CharField(
        source="campaign.name",
        read_only=True,
    )

    advertiser_name = serializers.CharField(
        source="campaign.advertiser.name",
        read_only=True,
    )

    advertiser_id = serializers.UUIDField(
        source="campaign.advertiser.id",
        read_only=True,
    )

    class Meta:
        model = Advertisement

        fields = [
            "id",

            "campaign",
            "campaign_name",

            "advertiser_id",
            "advertiser_name",

            "title",
            "description",

            "ad_type",

            "image",
            "video",

            "target_url",

            "placement",
            "pricing_model",
            "price",
            "duration",

            "is_active",

            "created_at",
            "updated_at",
        ]


class AdminAdvertisementStatsSerializer(
    serializers.Serializer
):
    impressions = serializers.IntegerField()

    clicks = serializers.IntegerField()

    ctr = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    completed = serializers.IntegerField()

    completion_rate = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    watched_seconds = serializers.IntegerField()

    average_watched_percentage = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


class AdminAdvertisementDailyStatsSerializer(
    serializers.Serializer
):
    date = serializers.DateField()

    impressions = serializers.IntegerField()

    clicks = serializers.IntegerField()

    completed = serializers.IntegerField()


class AdminAdvertisementFullDetailSerializer(
    serializers.Serializer
):
    advertisement = AdminAdvertisementDetailSerializer()

    stats = AdminAdvertisementStatsSerializer()

    daily_stats = AdminAdvertisementDailyStatsSerializer(
        many=True
    )