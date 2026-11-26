from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import UserListener
from .serializers import UserProfileSerializer , ChangePasswordSerializer

from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import SupportRequest
from .serializers import SupportRequestSerializer
from .throttles import (
    SupportAnonRateThrottle,
    SupportUserRateThrottle,
)

class SupportRequestCreateView(APIView):

    permission_classes = [
        AllowAny
    ]

    throttle_classes = [
        SupportAnonRateThrottle,
        SupportUserRateThrottle,
    ]

    def post(self, request):

        serializer = SupportRequestSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        support_request = serializer.save(
            user=(
                request.user
                if request.user.is_authenticated
                else None
            )
        )

        return Response(
            {
                "message": "درخواست پشتیبانی با موفقیت ثبت شد.",
                "request": SupportRequestSerializer(
                    support_request
                ).data,
            },
            status=status.HTTP_201_CREATED
        )

class MyProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return (
            UserListener.objects
            .select_related("wallet")
            .prefetch_related(
                "subscriptions__plan",
                "artist_subscriptions__artist",
                "artist_subscriptions__plan",
                "favorite_genres",
                "favorite_artists",
            )
            .get(
                pk=self.request.user.pk
            )
        )


class ChangePasswordView(generics.GenericAPIView):

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message": "رمز عبور با موفقیت تغییر کرد."
            },
            status=status.HTTP_200_OK,
        )


class MyProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):

        return (
            UserListener.objects
            .select_related("wallet")
            .prefetch_related(
                "subscriptions__plan",
                "artist_subscriptions__artist",
                "artist_subscriptions__plan",
                "favorite_genres",
                "favorite_artists",
            )
            .get(
                pk=self.request.user.pk
            )
        )
