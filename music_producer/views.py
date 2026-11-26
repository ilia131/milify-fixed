from django.core.files.storage import storages
from django.http import HttpResponseRedirect
from django.db import transaction
from django.db.models import F, Q

from rest_framework import generics, filters, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Beat,
    BeatLicense,
    BeatPurchase,
    ProducerProfile,
)

from .serializers import (
    BeatSerializer,
    BeatListSerializer,
    ProducerProfileSerializer,
    BeatPurchaseSerializer,
)

from subscriptions.models import (
    Wallet,
    WalletTransaction,
)

from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import transaction

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Beat,
    BeatLicense,
    BeatPurchase,
    ProducerProfile,
)

from subscriptions.models import (
    Wallet,
    WalletTransaction,
)

from subscriptions.models import PlatformRevenue
import os
import re

import os
import re

from django.http import HttpResponse, StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import BeatPurchase


class StreamPurchasedBeatView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, purchase_id):

        # =====================================================
        # GET PURCHASE
        # =====================================================

        try:

            purchase = (
                BeatPurchase.objects
                .select_related(
                    "beat",
                    "license",
                )
                .get(
                    id=purchase_id,
                    user=request.user,
                    status="COMPLETED",
                )
            )

        except BeatPurchase.DoesNotExist:

            return HttpResponse(
                "Purchase not found.",
                status=status.HTTP_404_NOT_FOUND,
            )

        # =====================================================
        # LICENSE
        # =====================================================

        license_obj = purchase.license

        if license_obj is None:

            return HttpResponse(
                "License not found.",
                status=status.HTTP_404_NOT_FOUND,
            )

        # =====================================================
        # AUDIO FILE
        # =====================================================

        if not license_obj.audio_file:

            return HttpResponse(
                "Audio file not found.",
                status=status.HTTP_404_NOT_FOUND,
            )

        # =====================================================
        # LOCAL FILE PATH
        # =====================================================

        try:

            path = license_obj.audio_file.path

        except NotImplementedError:
            response = HttpResponseRedirect(storages["private_tracks"].url(license_obj.audio_file.name))
            response["Cache-Control"] = "private, no-store"
            return response

        except (ValueError, AttributeError):

            return HttpResponse(
                "Audio file is not available locally.",
                status=status.HTTP_404_NOT_FOUND,
            )

        # =====================================================
        # SECURITY
        # =====================================================

        media_root = os.path.abspath(
            str(
                license_obj.audio_file.storage.location
            )
        )

        path = os.path.abspath(
            path
        )

        # Prevent path traversal
        if not path.startswith(
            media_root + os.sep
        ):

            return HttpResponse(
                "Invalid audio path.",
                status=status.HTTP_403_FORBIDDEN,
            )

        # =====================================================
        # FILE EXISTS
        # =====================================================

        if not os.path.isfile(path):

            return HttpResponse(
                "Audio file not found.",
                status=status.HTTP_404_NOT_FOUND,
            )

        # =====================================================
        # FILE SIZE
        # =====================================================

        file_size = os.path.getsize(
            path
        )

        if file_size <= 0:

            return HttpResponse(
                "Audio file is empty.",
                status=status.HTTP_404_NOT_FOUND,
            )

        # =====================================================
        # CONTENT TYPE
        # =====================================================

        content_type = (
            "audio/mpeg"
        )

        extension = (
            os.path.splitext(path)[1]
            .lower()
        )

        if extension == ".wav":
            content_type = "audio/wav"

        elif extension == ".ogg":
            content_type = "audio/ogg"

        elif extension == ".flac":
            content_type = "audio/flac"

        elif extension == ".m4a":
            content_type = "audio/mp4"

        # =====================================================
        # RANGE HEADER
        # =====================================================

        range_header = request.headers.get(
            "Range"
        )

        # =====================================================
        # NO RANGE
        # =====================================================

        if not range_header:

            audio_file = open(
                path,
                "rb",
            )

            response = StreamingHttpResponse(
                audio_file,
                status=status.HTTP_200_OK,
                content_type=content_type,
            )

            response["Content-Length"] = str(
                file_size
            )

            response["Accept-Ranges"] = "bytes"

            response["Content-Disposition"] = (
                f'inline; filename="{os.path.basename(path)}"'
            )

            response["Cache-Control"] = (
                "private, no-store"
            )

            return response

        # =====================================================
        # PARSE RANGE
        # =====================================================

        range_match = re.match(
            r"^bytes=(\d*)-(\d*)$",
            range_header.strip(),
        )

        if not range_match:

            response = HttpResponse(
                status=(
                    status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
                )
            )

            response["Content-Range"] = (
                f"bytes */{file_size}"
            )

            return response

        start_str = (
            range_match.group(1)
        )

        end_str = (
            range_match.group(2)
        )

        # =====================================================
        # RANGE: bytes=-500
        # =====================================================

        if not start_str:

            if not end_str:

                response = HttpResponse(
                    status=(
                        status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
                    )
                )

                response["Content-Range"] = (
                    f"bytes */{file_size}"
                )

                return response

            suffix_length = int(
                end_str
            )

            if suffix_length <= 0:

                response = HttpResponse(
                    status=(
                        status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
                    )
                )

                response["Content-Range"] = (
                    f"bytes */{file_size}"
                )

                return response

            suffix_length = min(
                suffix_length,
                file_size,
            )

            start = (
                file_size -
                suffix_length
            )

            end = (
                file_size -
                1
            )

        # =====================================================
        # RANGE: bytes=100-
        # =====================================================

        else:

            start = int(
                start_str
            )

            if start >= file_size:

                response = HttpResponse(
                    status=(
                        status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
                    )
                )

                response["Content-Range"] = (
                    f"bytes */{file_size}"
                )

                return response

            # =================================================
            # END
            # =================================================

            if end_str:

                end = int(
                    end_str
                )

            else:

                end = (
                    file_size -
                    1
                )

            # =================================================
            # CLAMP END
            # =================================================

            end = min(
                end,
                file_size - 1,
            )

        # =====================================================
        # VALIDATE RANGE
        # =====================================================

        if start < 0 or start > end:

            response = HttpResponse(
                status=(
                    status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
                )
            )

            response["Content-Range"] = (
                f"bytes */{file_size}"
            )

            return response

        # =====================================================
        # CONTENT LENGTH
        # =====================================================

        content_length = (
            end -
            start +
            1
        )

        # =====================================================
        # OPEN FILE
        # =====================================================

        audio_file = open(
            path,
            "rb",
        )

        audio_file.seek(
            start
        )

        # =====================================================
        # PARTIAL RESPONSE
        # =====================================================

        response = StreamingHttpResponse(
            audio_file,
            status=status.HTTP_206_PARTIAL_CONTENT,
            content_type=content_type,
        )

        response["Content-Length"] = str(
            content_length
        )

        response["Content-Range"] = (
            f"bytes {start}-{end}/{file_size}"
        )

        response["Accept-Ranges"] = "bytes"

        response["Content-Disposition"] = (
            f'inline; filename="{os.path.basename(path)}"'
        )

        response["Cache-Control"] = (
            "private, no-store"
        )

        return response
# =========================================================
# BEATS
# =========================================================


class BeatListView(generics.ListAPIView):

    serializer_class = BeatListSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "title",
        "producer__producer_name",
        "genre",
    ]

    ordering_fields = [
        "created_at",
        "price",
        "plays",
        "sales",
    ]

    ordering = [
        "-created_at"
    ]

    def get_queryset(self):

        queryset = (
            Beat.objects
            .filter(
                is_active=True,
                producer__is_active=True,
            )
            .select_related(
                "producer",
                "producer__user",
            )
        )

        genre = self.request.query_params.get("genre")

        if genre:
            queryset = queryset.filter(
                genre=genre.upper()
            )

        featured = self.request.query_params.get("featured")

        if featured == "true":
            queryset = queryset.filter(
                is_featured=True
            )

        return queryset


class BeatDetailView(generics.RetrieveAPIView):

    serializer_class = BeatSerializer

    lookup_field = "id"

    def get_queryset(self):

        return (
            Beat.objects
            .filter(
                is_active=True,
                producer__is_active=True,
            )
            .select_related(
                "producer",
                "producer__user",
            )
            .prefetch_related(
                "licenses"
            )
        )


# =========================================================
# PRODUCER PROFILE
# =========================================================


class ProducerProfileListView(generics.ListAPIView):

    serializer_class = ProducerProfileSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "producer_name",
        "bio",
    ]

    ordering_fields = [
        "created_at",
        "total_sales",
        "total_revenue",
    ]

    ordering = [
        "-created_at"
    ]

    def get_queryset(self):

        return (
            ProducerProfile.objects
            .filter(
                is_active=True
            )
            .select_related(
                "user"
            )
        )


class ProducerProfileDetailView(generics.RetrieveAPIView):

    serializer_class = ProducerProfileSerializer

    lookup_field = "uuid"

    def get_queryset(self):

        return (
            ProducerProfile.objects
            .filter(
                is_active=True
            )
            .select_related(
                "user"
            )
        )


class ProducerBeatListView(generics.ListAPIView):

    serializer_class = BeatListSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "title",
        "genre",
    ]

    ordering_fields = [
        "created_at",
        "price",
        "plays",
        "sales",
    ]

    ordering = [
        "-created_at"
    ]

    def get_queryset(self):

        producer_uuid = self.kwargs["uuid"]

        return (
            Beat.objects
            .filter(
                producer__uuid=producer_uuid,
                producer__is_active=True,
                is_active=True,
            )
            .select_related(
                "producer",
                "producer__user",
            )
        )


# =========================================================
# BUY BEAT LICENSE
# =========================================================





class BuyBeatView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @transaction.atomic
    def post(self, request, beat_id):

        # =====================================================
        # GET BEAT
        # =====================================================

        try:

            beat = (
                Beat.objects
                .select_related(
                    "producer",
                    "producer__user",
                )
                .select_for_update(of=("self",))
                .get(
                    id=beat_id,
                    is_active=True,
                    producer__is_active=True,
                )
            )

        except Beat.DoesNotExist:

            return Response(
                {
                    "detail": "بیت پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # =====================================================
        # PREVENT BUYING OWN BEAT
        # =====================================================

        if beat.producer.user_id == request.user.id:

            return Response(
                {
                    "detail": "شما نمی‌توانید بیت خودتان را خریداری کنید."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =====================================================
        # LICENSE
        # =====================================================

        license_id = serializers.IntegerField(min_value=1).run_validation(
            request.data.get("license_id")
        )

        try:

            license_obj = (
                BeatLicense.objects
                .select_for_update()
                .get(
                    id=license_id,
                    beat=beat,
                    is_active=True,
                )
            )

        except BeatLicense.DoesNotExist:

            return Response(
                {
                    "detail": "لایسنس معتبر نیست."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # =====================================================
        # CHECK PREVIOUS PURCHASE
        # =====================================================

        already_purchased = (
            BeatPurchase.objects
            .filter(
                user=request.user,
                beat=beat,
                status="COMPLETED",
            )
            .exists()
        )

        if already_purchased:

            return Response(
                {
                    "detail": "این بیت را قبلاً خریداری کرده‌اید."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        producer = beat.producer
        wallet_users = sorted([request.user.pk, producer.user_id])
        wallets = {}
        for user_id in wallet_users:
            wallet, _ = Wallet.objects.select_for_update().get_or_create(user_id=user_id)
            wallets[user_id] = wallet
        buyer_wallet = wallets[request.user.pk]
        producer_wallet = wallets[producer.user_id]

        # =====================================================
        # PRICE
        # =====================================================

        price = Decimal(
            str(license_obj.price)
        )

        # =====================================================
        # INVALID PRICE PROTECTION
        # =====================================================

        if price <= Decimal("0"):

            return Response(
                {
                    "detail": "قیمت این لایسنس معتبر نیست."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =====================================================
        # CHECK BALANCE
        # =====================================================

        if buyer_wallet.balance < price:

            required = (
                price -
                buyer_wallet.balance
            )

            return Response(
                {
                    "detail": "موجودی کیف پول کافی نیست.",
                    "balance": buyer_wallet.balance,
                    "price": price,
                    "required": required,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =====================================================
        # PLATFORM FEE
        # =====================================================

        fee_percent = Decimal(
            str(
                getattr(
                    settings,
                    "MILIFY_BEAT_PLATFORM_FEE_PERCENT",
                    "20",
                )
            )
        )

        # =====================================================
        # VALIDATE FEE
        # =====================================================

        if fee_percent < Decimal("0"):

            fee_percent = Decimal("0")

        if fee_percent > Decimal("100"):

            fee_percent = Decimal("100")

        # =====================================================
        # CALCULATE REVENUE
        # =====================================================

        platform_fee = (price * fee_percent / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        producer_revenue = (
            price -
            platform_fee
        )

        # =====================================================
        # SAVE OLD BALANCES
        # =====================================================

        old_buyer_balance = (
            buyer_wallet.balance
        )

        old_producer_balance = (
            producer_wallet.balance
        )

        # =====================================================
        # BUYER BALANCE
        # =====================================================

        buyer_wallet.balance = (
            buyer_wallet.balance -
            price
        )

        buyer_wallet.save(
            update_fields=[
                "balance",
                "updated_at",
            ]
        )

        # =====================================================
        # PRODUCER BALANCE
        # =====================================================

        producer_wallet.balance = (
            producer_wallet.balance +
            producer_revenue
        )

        producer_wallet.save(
            update_fields=[
                "balance",
                "updated_at",
            ]
        )

        # =====================================================
        # PURCHASE
        # =====================================================

        purchase = (
            BeatPurchase.objects
            .create(

                user=request.user,

                beat=beat,

                license=license_obj,

                price=price,

                platform_fee=platform_fee,

                producer_revenue=producer_revenue,

                status="COMPLETED",
            )
        )

        # =====================================================
        # BUYER TRANSACTION
        # =====================================================

        WalletTransaction.objects.create(

            wallet=buyer_wallet,

            amount=-price,

            transaction_type="BEAT_PURCHASE",

            description=(
                f"خرید بیت "
                f"{beat.title} - "
                f"{license_obj.name}"
            ),
        )

        # =====================================================
        # PRODUCER TRANSACTION
        # =====================================================

        WalletTransaction.objects.create(

            wallet=producer_wallet,

            amount=producer_revenue,

            transaction_type="BEAT_REVENUE",

            description=(
                f"درآمد فروش بیت "
                f"{beat.title} - "
                f"{license_obj.name}"
            ),
        )

        # =====================================================
        # PLATFORM REVENUE
        # =====================================================

        PlatformRevenue.objects.create(

            revenue_type="BEAT_SALE",

            amount=platform_fee,

            purchase=purchase,

            description=(
                f"کارمزد Milify از فروش "
                f"{beat.title} - "
                f"{license_obj.name}"
            ),
        )

        # =====================================================
        # UPDATE BEAT SALES
        # =====================================================

        beat.sales = (
            beat.sales +
            1
        )

        beat.save(
            update_fields=[
                "sales"
            ]
        )

        # =====================================================
        # UPDATE PRODUCER STATISTICS
        # =====================================================

        ProducerProfile.objects.filter(pk=producer.pk).update(
            total_sales=F("total_sales") + 1,
            total_revenue=F("total_revenue") + producer_revenue,
        )

        # =====================================================
        # RESPONSE
        # =====================================================

        return Response(

            {
                "message": (
                    "بیت با موفقیت خریداری شد."
                ),

                "purchase": {

                    "id": str(
                        purchase.id
                    ),

                    "beat_id": (
                        beat.id
                    ),

                    "beat_title": (
                        beat.title
                    ),

                    "license_id": (
                        license_obj.id
                    ),

                    "license_name": (
                        license_obj.name
                    ),

                    "license_type": (
                        license_obj.license_type
                    ),

                    "price": (
                        price
                    ),

                    "platform_fee": (
                        platform_fee
                    ),

                    "producer_revenue": (
                        producer_revenue
                    ),

                    "status": (
                        purchase.status
                    ),
                },

                "buyer_wallet": {

                    "old_balance": (
                        old_buyer_balance
                    ),

                    "remaining_balance": (
                        buyer_wallet.balance
                    ),
                },

                "producer": {

                    "uuid": str(
                        producer.uuid
                    ),

                    "producer_name": (
                        producer.producer_name
                    ),
                },

                "producer_wallet": {

                    "old_balance": (
                        old_producer_balance
                    ),

                    "new_balance": (
                        producer_wallet.balance
                    ),
                },

                "platform": {

                    "fee_percent": (
                        fee_percent
                    ),

                    "revenue": (
                        platform_fee
                    ),
                },
            },

            status=status.HTTP_201_CREATED,
        )

# =========================================================
# MY PURCHASES
# =========================================================


class MyBeatPurchasesView(generics.ListAPIView):

    permission_classes = [
        IsAuthenticated
    ]

    serializer_class = BeatPurchaseSerializer

    def get_queryset(self):

        return (
            BeatPurchase.objects
            .filter(
                user=self.request.user,
                status="COMPLETED",
            )
            .select_related(
                "beat",
                "beat__producer",
                "beat__producer__user",
            )
            .prefetch_related(
                "beat__licenses"
            )
            .order_by(
                "-created_at"
            )
        )
        
        
        

class DownloadBeatView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request,
        purchase_id,
    ):

        try:

            purchase = (
                BeatPurchase.objects
                .select_related(
                    "license",
                    "beat",
                )
                .get(
                    id=purchase_id,
                    user=request.user,
                    status="COMPLETED",
                )
            )

        except BeatPurchase.DoesNotExist:

            return Response(
                {
                    "detail": "خرید پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )


        if not purchase.license:

            return Response(
                {
                    "detail": "لایسنس خریداری‌شده پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )


        if not purchase.license.audio_file:

            return Response(
                {
                    "detail": "فایل این لایسنس موجود نیست."
                },
                status=status.HTTP_404_NOT_FOUND,
            )


        return Response(
            {
                "beat": purchase.beat.title,

                "license": (
                    purchase.license.name
                ),

                "audio_file": (
                    request.build_absolute_uri(
                        storages["private_tracks"].url(purchase.license.audio_file.name)
                    )
                ),
            }
        )