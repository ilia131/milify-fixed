from decimal import Decimal

from django.db.models import (
    Q,
    Count,
    Avg,
    Sum,
    Value,
    FloatField,
)

from django.db.models.functions import (
    TruncDay,
    Coalesce,
)

from django.utils import timezone

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
    JSONParser,
)

from .models import (
    Advertisement,
    AdImpression,
    AdClick,
)

from .admin_serializers import (
    AdminAdvertisementListSerializer,
    AdminAdvertisementDetailSerializer,
    AdminAdvertisementCreateUpdateSerializer,
    AdminAdvertisementFullDetailSerializer,
)

from .admin_pagination import (
    AdminAdvertisementPagination,
)


# =========================================================
# ADMIN ADVERTISEMENT LIST + CREATE
# =========================================================

class AdminAdvertisementListCreateView(
    generics.ListCreateAPIView
):

    permission_classes = [
        IsAdminUser
    ]

    pagination_class = (
        AdminAdvertisementPagination
    )

    def get_queryset(self):

        queryset = (
            Advertisement.objects
            .select_related(
                "campaign",
                "campaign__advertiser",
            )
            .order_by("-created_at")
        )

        # =====================================================
        # SEARCH
        # =====================================================

        search = self.request.query_params.get(
            "search"
        )

        if search:

            search = search.strip()

            if search:

                queryset = queryset.filter(
                    Q(
                        title__icontains=search
                    )
                    |
                    Q(
                        description__icontains=search
                    )
                    |
                    Q(
                        campaign__name__icontains=search
                    )
                    |
                    Q(
                        campaign__advertiser__name__icontains=search
                    )
                )

        # =====================================================
        # AD TYPE
        # =====================================================

        ad_type = (
            self.request.query_params.get(
                "ad_type"
            )
        )

        if ad_type:

            queryset = queryset.filter(
                ad_type=ad_type.upper()
            )

        # =====================================================
        # PLACEMENT
        # =====================================================

        placement = (
            self.request.query_params.get(
                "placement"
            )
        )

        if placement:

            queryset = queryset.filter(
                placement=placement.upper()
            )

        # =====================================================
        # PRICING MODEL
        # =====================================================

        pricing_model = (
            self.request.query_params.get(
                "pricing_model"
            )
        )

        if pricing_model:

            queryset = queryset.filter(
                pricing_model=pricing_model.upper()
            )

        # =====================================================
        # ACTIVE
        # =====================================================

        is_active = (
            self.request.query_params.get(
                "is_active"
            )
        )

        if is_active is not None:

            if is_active.lower() in [
                "true",
                "1",
            ]:

                queryset = queryset.filter(
                    is_active=True
                )

            elif is_active.lower() in [
                "false",
                "0",
            ]:

                queryset = queryset.filter(
                    is_active=False
                )

        # =====================================================
        # CAMPAIGN
        # =====================================================

        campaign = (
            self.request.query_params.get(
                "campaign"
            )
        )

        if campaign:

            queryset = queryset.filter(
                campaign_id=campaign
            )

        return queryset

    def get_serializer_class(self):

        if self.request.method == "POST":

            return (
                AdminAdvertisementCreateUpdateSerializer
            )

        return (
            AdminAdvertisementListSerializer
        )


# =========================================================
# ADMIN ADVERTISEMENT DETAIL
# =========================================================

class AdminAdvertisementDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    permission_classes = [
        IsAdminUser
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    lookup_field = "id"

    def get_queryset(self):

        return (
            Advertisement.objects
            .select_related(
                "campaign",
                "campaign__advertiser",
            )
        )

    def get_serializer_class(self):

        if self.request.method in [
            "PUT",
            "PATCH",
        ]:

            return (
                AdminAdvertisementCreateUpdateSerializer
            )

        return (
            AdminAdvertisementDetailSerializer
        )


# =========================================================
# ADMIN ADVERTISEMENT STATS
# =========================================================

class AdminAdvertisementStatsView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAdminUser
    ]

    def get(self, request, id):

        # =====================================================
        # ADVERTISEMENT
        # =====================================================

        try:

            advertisement = (
                Advertisement.objects
                .select_related(
                    "campaign",
                    "campaign__advertiser",
                )
                .get(
                    id=id
                )
            )

        except Advertisement.DoesNotExist:

            raise NotFound(
                "Advertisement not found."
            )

        # =====================================================
        # DAYS
        # =====================================================

        days = request.query_params.get(
            "days",
            "30",
        )

        try:

            days = int(days)

        except (
            TypeError,
            ValueError,
        ):

            days = 30

        days = max(
            1,
            min(
                days,
                365,
            )
        )

        # =====================================================
        # DATE RANGE
        # =====================================================

        now = timezone.now()

        today_start = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        start_date = (
            today_start
            - timezone.timedelta(
                days=days - 1
            )
        )

        # =====================================================
        # IMPRESSIONS
        # =====================================================

        impressions = (
            AdImpression.objects
            .filter(
                ad=advertisement,
                created_at__gte=start_date,
            )
        )

        # =====================================================
        # CLICKS
        # =====================================================

        clicks = (
            AdClick.objects
            .filter(
                ad=advertisement,
                created_at__gte=start_date,
            )
        )

        # =====================================================
        # COUNTS
        # =====================================================

        impression_count = (
            impressions.count()
        )

        click_count = (
            clicks.count()
        )

        completed_count = (
            impressions
            .filter(
                completed=True
            )
            .count()
        )

        # =====================================================
        # WATCHED SECONDS
        # =====================================================

        watched_seconds = (
            impressions
            .aggregate(
                total=Coalesce(
                    Sum(
                        "watched_seconds",
                        output_field=FloatField(),
                    ),
                    Value(
                        0.0,
                        output_field=FloatField(),
                    ),
                    output_field=FloatField(),
                )
            )
            ["total"]
            or 0.0
        )

        # =====================================================
        # AVERAGE WATCHED
        # =====================================================

        average_watched_percentage = (
            impressions
            .aggregate(
                average=Coalesce(
                    Avg(
                        "watched_percentage",
                        output_field=FloatField(),
                    ),
                    Value(
                        0.0,
                        output_field=FloatField(),
                    ),
                    output_field=FloatField(),
                )
            )
            ["average"]
            or 0.0
        )

        # =====================================================
        # CTR
        # =====================================================

        if impression_count:

            ctr = (
                Decimal(click_count)
                /
                Decimal(impression_count)
            ) * Decimal("100")

        else:

            ctr = Decimal("0")

        # =====================================================
        # COMPLETION RATE
        # =====================================================

        if impression_count:

            completion_rate = (
                Decimal(completed_count)
                /
                Decimal(impression_count)
            ) * Decimal("100")

        else:

            completion_rate = Decimal("0")

        # =====================================================
        # DAILY IMPRESSIONS
        # =====================================================

        daily_impressions = (
            impressions
            .annotate(
                date=TruncDay(
                    "created_at"
                )
            )
            .values(
                "date"
            )
            .annotate(
                impressions=Count(
                    "id"
                )
            )
            .order_by(
                "date"
            )
        )

        # =====================================================
        # DAILY CLICKS
        # =====================================================

        daily_clicks = (
            clicks
            .annotate(
                date=TruncDay(
                    "created_at"
                )
            )
            .values(
                "date"
            )
            .annotate(
                clicks=Count(
                    "id"
                )
            )
            .order_by(
                "date"
            )
        )

        # =====================================================
        # DAILY COMPLETED
        # =====================================================

        daily_completed = (
            impressions
            .filter(
                completed=True
            )
            .annotate(
                date=TruncDay(
                    "created_at"
                )
            )
            .values(
                "date"
            )
            .annotate(
                completed=Count(
                    "id"
                )
            )
            .order_by(
                "date"
            )
        )

        # =====================================================
        # MAPS
        # =====================================================

        impressions_map = {
            item["date"]
            .date()
            .isoformat():
                item["impressions"]
            for item in daily_impressions
        }

        clicks_map = {
            item["date"]
            .date()
            .isoformat():
                item["clicks"]
            for item in daily_clicks
        }

        completed_map = {
            item["date"]
            .date()
            .isoformat():
                item["completed"]
            for item in daily_completed
        }

        # =====================================================
        # DAILY STATS
        # =====================================================

        daily_stats = []

        for index in range(days):

            date = (
                start_date
                +
                timezone.timedelta(
                    days=index
                )
            ).date()

            date_key = date.isoformat()

            daily_stats.append(
                {
                    "date": date,

                    "impressions":
                        impressions_map.get(
                            date_key,
                            0,
                        ),

                    "clicks":
                        clicks_map.get(
                            date_key,
                            0,
                        ),

                    "completed":
                        completed_map.get(
                            date_key,
                            0,
                        ),
                }
            )

        # =====================================================
        # RESPONSE
        # =====================================================

        data = {

            "advertisement":
                advertisement,

            "stats": {

                "impressions":
                    impression_count,

                "clicks":
                    click_count,

                "ctr":
                    round(
                        ctr,
                        2,
                    ),

                "completed":
                    completed_count,

                "completion_rate":
                    round(
                        completion_rate,
                        2,
                    ),

                "watched_seconds":
                    round(
                        watched_seconds,
                        2,
                    ),

                "average_watched_percentage":
                    round(
                        average_watched_percentage,
                        2,
                    ),
            },

            "daily_stats":
                daily_stats,
        }

        serializer = (
            AdminAdvertisementFullDetailSerializer(
                instance=data
            )
        )

        return Response(
            serializer.data
        )
