from django.db import transaction
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAdminUser, SAFE_METHODS

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    Advertiser,
    Campaign,
    Advertisement,
    AdImpression,
    AdClick,
)

from .serializers import (
    AdvertiserSerializer,
    CampaignSerializer,
    AdvertisementSerializer,
)


class AdvertiserListCreateView(APIView):
    def get_permissions(self):
        permission = AllowAny if self.request.method in SAFE_METHODS else IsAdminUser
        return [permission()]


    def get(self, request):

        advertisers = Advertiser.objects.filter(
            is_active=True
        ).order_by("-created_at")

        serializer = AdvertiserSerializer(
            advertisers,
            many=True,
            context={"request": request}
        )

        return Response(
            serializer.data
        )

    def post(self, request):

        serializer = AdvertiserSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        advertiser = serializer.save()

        return Response(
            AdvertiserSerializer(
                advertiser,
                context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED
        )


class CampaignListCreateView(APIView):
    def get_permissions(self):
        permission = AllowAny if self.request.method in SAFE_METHODS else IsAdminUser
        return [permission()]


    def get(self, request):

        campaigns = Campaign.objects.select_related(
            "advertiser"
        ).order_by("-created_at")

        serializer = CampaignSerializer(
            campaigns,
            many=True
        )

        return Response(
            serializer.data
        )

    def post(self, request):

        serializer = CampaignSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        campaign = serializer.save()

        return Response(
            CampaignSerializer(campaign).data,
            status=status.HTTP_201_CREATED
        )





def active_ads():
    now = timezone.now()
    return Advertisement.objects.select_related("campaign__advertiser").filter(
        is_active=True,
        campaign__advertiser__is_active=True,
        campaign__status="ACTIVE",
        campaign__start_at__lte=now,
        campaign__end_at__gte=now,
    )


class AdvertisementListCreateView(APIView):
    def get(self, request):
        if request.user.is_authenticated and request.user.has_active_subscription:
            return Response([])

        ads = active_ads()
        placement = request.query_params.get("placement", "").strip()
        if placement:
            ads = ads.filter(placement__iexact=placement)
        return Response(AdvertisementSerializer(ads, many=True, context={"request": request}).data)


class AdvertisementDetailView(APIView):
    def get(self, request, pk):
        ad = get_object_or_404(active_ads(), pk=pk)
        return Response(AdvertisementSerializer(ad, context={"request": request}).data)


class AdSessionSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()


class AdProgressSerializer(AdSessionSerializer):
    watched_seconds = serializers.IntegerField(min_value=0, max_value=2147483647, default=0)
    watched_percentage = serializers.IntegerField(min_value=0, max_value=100, default=0)
    completed = serializers.BooleanField(default=False)


class AdImpressionView(APIView):
    @transaction.atomic
    def post(self, request, ad_id):
        serializer = AdProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        progress = serializer.validated_data
        ad = get_object_or_404(active_ads().select_for_update(of=("self",)), pk=ad_id)
        user = request.user if request.user.is_authenticated else None
        session_id = progress.pop("session_id")

        impression = AdImpression.objects.filter(ad=ad, user=user, session_id=session_id).first()
        if impression is None:
            impression = AdImpression.objects.create(
                ad=ad, user=user, session_id=session_id, **progress
            )
            response_status = status.HTTP_201_CREATED
        else:
            impression.watched_seconds = max(impression.watched_seconds, progress["watched_seconds"])
            impression.watched_percentage = max(
                impression.watched_percentage, progress["watched_percentage"]
            )
            impression.completed = impression.completed or progress["completed"]
            impression.save(update_fields=["watched_seconds", "watched_percentage", "completed"])
            response_status = status.HTTP_200_OK

        return Response(
            {"status": "ok", "impression_id": str(impression.id)}, status=response_status
        )


class AdClickView(APIView):
    @transaction.atomic
    def post(self, request, ad_id):
        serializer = AdSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ad = get_object_or_404(active_ads().select_for_update(of=("self",)), pk=ad_id)
        user = request.user if request.user.is_authenticated else None
        session_id = serializer.validated_data["session_id"]

        click = AdClick.objects.filter(ad=ad, user=user, session_id=session_id).first()
        if click is None:
            click = AdClick.objects.create(ad=ad, user=user, session_id=session_id)
            response_status = status.HTTP_201_CREATED
        else:
            response_status = status.HTTP_200_OK

        return Response(
            {"status": "ok", "target_url": ad.target_url, "click_id": str(click.id)},
            status=response_status,
        )
