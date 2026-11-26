from django.db.models import (
    Count,
    Q,
    Sum,
)

from django.db.models.functions import (
    TruncDay,
)

from django.utils import timezone

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .admin_pagination import AdminPaymentPagination , AdminSubscriptionPagination
from .models import (
    Payment,
    Subscription,
)

from .admin_serializers import (
    AdminPaymentSerializer,
    AdminSubscriptionSerializer,
)


class AdminPaymentListView(generics.ListAPIView):
    """
    Admin:
    List all payments.
    """

    serializer_class = AdminPaymentSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminPaymentPagination

    def get_queryset(self):
        queryset = (
            Payment.objects
            .select_related(
                "user",
                "subscription",
                "subscription__plan",
                "artist_subscription",
                "artist_subscription__plan",
            )
            .order_by("-created_at")
        )

        search = self.request.query_params.get("search")

        status_filter = self.request.query_params.get(
            "status"
        )

        payment_type = self.request.query_params.get(
            "type"
        )

        if search:
            search = search.strip()

            queryset = queryset.filter(
                Q(user__username__icontains=search)
                | Q(user__email__icontains=search)
                | Q(authority__icontains=search)
                | Q(ref_id__icontains=search)
            )

        if status_filter:
            queryset = queryset.filter(
                status=status_filter.upper()
            )

        if payment_type == "PLATFORM":
            queryset = queryset.filter(
                subscription__isnull=False
            )

        elif payment_type == "ARTIST":
            queryset = queryset.filter(
                artist_subscription__isnull=False
            )

        return queryset


class AdminSubscriptionListView(generics.ListAPIView):
    """
    Admin:
    List all platform subscriptions.
    """

    serializer_class = AdminSubscriptionSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminSubscriptionPagination

    def get_queryset(self):
        queryset = (
            Subscription.objects
            .select_related(
                "user",
                "plan",
            )
            .order_by("-created_at")
        )

        search = self.request.query_params.get("search")

        status_filter = self.request.query_params.get(
            "status"
        )

        if search:
            search = search.strip()

            queryset = queryset.filter(
                Q(user__username__icontains=search)
                | Q(user__email__icontains=search)
                | Q(plan__name__icontains=search)
            )

        if status_filter:
            queryset = queryset.filter(
                status=status_filter.upper()
            )

        return queryset
    
    
    
class AdminRevenueView(APIView):
    """
    Admin:
    Revenue overview.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):

        now = timezone.now()

        today_start = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        month_start = now.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        successful_payments = Payment.objects.filter(
            status="SUCCESS"
        )

        total_revenue = (
            successful_payments.aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        today_revenue = (
            successful_payments
            .filter(
                paid_at__gte=today_start
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        monthly_revenue = (
            successful_payments
            .filter(
                paid_at__gte=month_start
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        platform_revenue = (
            successful_payments
            .filter(
                subscription__isnull=False
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        artist_revenue = (
            successful_payments
            .filter(
                artist_subscription__isnull=False
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        successful_count = (
            successful_payments.count()
        )

        pending_count = Payment.objects.filter(
            status="PENDING"
        ).count()

        failed_count = Payment.objects.filter(
            status="FAILED"
        ).count()

        active_subscriptions = (
            Subscription.objects.filter(
                status="ACTIVE",
                expires_at__gt=now,
            ).count()
        )

        return Response({
            "total_revenue": total_revenue,
            "today_revenue": today_revenue,
            "monthly_revenue": monthly_revenue,

            "platform_revenue": platform_revenue,
            "artist_revenue": artist_revenue,

            "successful_payments": successful_count,
            "pending_payments": pending_count,
            "failed_payments": failed_count,

            "active_subscriptions": active_subscriptions,
        })
        
        

class AdminRevenueChartView(APIView):
    """
    Admin:
    Daily revenue for the last 30 days.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):

        now = timezone.now()

        start_date = now - timezone.timedelta(
            days=30
        )

        revenue = (
            Payment.objects
            .filter(
                status="SUCCESS",
                paid_at__gte=start_date,
            )
            .annotate(
                date=TruncDay("paid_at")
            )
            .values("date")
            .annotate(
                revenue=Sum("amount")
            )
            .order_by("date")
        )

        data = [
            {
                "date": item["date"],
                "revenue": item["revenue"],
            }
            for item in revenue
        ]

        return Response(data)