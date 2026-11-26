import uuid

import requests
from django.conf import settings
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.models import UserListener
from .serializers import FavoriteArtistsSerializer


class ListenerViewSet(UserViewSet):
    lookup_value_regex = r"[0-9]+"

    def get_throttles(self):
        self.throttle_scope = "registration" if self.action == "create" else None
        return [*super().get_throttles(), ScopedRateThrottle()]


class GoogleTokenLoginView(APIView):

    authentication_classes = []
    permission_classes = []

    parser_classes = (
        JSONParser,
        FormParser,
        MultiPartParser,
    )

    GOOGLE_TOKENINFO_URL = (
        "https://oauth2.googleapis.com/tokeninfo"
    )

    def post(self, request):

        google_token = request.data.get("id_token")

        if not google_token:
            return Response(
                {
                    "detail": "Google id_token is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =====================================================
        # VERIFY GOOGLE TOKEN
        # =====================================================

        try:
            google_response = requests.get(
                self.GOOGLE_TOKENINFO_URL,
                params={
                    "id_token": google_token,
                },
                timeout=10,
            )

        except requests.RequestException:

            return Response(
                {
                    "detail": "Google verification service unavailable."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if google_response.status_code != 200:

            return Response(
                {
                    "detail": "Invalid Google token."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            google_data = google_response.json()

        except ValueError:

            print(
                "GOOGLE TOKENINFO INVALID JSON"
            )

            return Response(
                {
                    "detail": "Invalid Google response."
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # =====================================================
        # VERIFY AUDIENCE
        # =====================================================

        expected_client_id = (
            settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        )

        if not expected_client_id or google_data.get("aud") != expected_client_id:

            print(
                "GOOGLE AUDIENCE MISMATCH:",
                google_data.get("aud"),
            )

            return Response(
                {
                    "detail": "Invalid Google token audience."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # =====================================================
        # VERIFY ISSUER
        # =====================================================

        if google_data.get("iss") not in (
            "https://accounts.google.com",
            "accounts.google.com",
        ):

            return Response(
                {
                    "detail": "Invalid Google token issuer."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # =====================================================
        # VERIFY EMAIL
        # =====================================================

        email = google_data.get("email")

        if not email:

            return Response(
                {
                    "detail": "Google email not found."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if str(
            google_data.get("email_verified")
        ).lower() != "true":

            return Response(
                {
                    "detail": "Google email is not verified."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # =====================================================
        # GOOGLE DATA
        # =====================================================

        email = email.lower().strip()

        first_name = google_data.get(
            "given_name",
            "",
        )

        last_name = google_data.get(
            "family_name",
            "",
        )

        # =====================================================
        # FIND USER
        # =====================================================

        user = UserListener.objects.filter(
            email=email
        ).first()

        created = False

        # =====================================================
        # CREATE GOOGLE USER
        # =====================================================

        if user is None:

            base_username = email.split("@")[0]

            username = base_username

            while UserListener.objects.filter(
                username=username
            ).exists():

                username = (
                    f"{base_username}_"
                    f"{uuid.uuid4().hex[:6]}"
                )

            user = UserListener.objects.create_user(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )

            created = True

        if not user.is_active:
            return Response(
                {"detail": "This account is inactive."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # =====================================================
        # JWT
        # =====================================================

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # =====================================================
        # RESPONSE
        # =====================================================

        return Response(
            {
                "access": str(access),
                "refresh": str(refresh),

                "created": created,

                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            },
            status=status.HTTP_200_OK,
        )




class GoogleProfileCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FavoriteArtistsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.favorite_artists.set(serializer.validated_data["favorite_artists"])
        return Response({"detail": "Updated favorite artists.", **serializer.data})


def set_token_cookie(response, name, token, max_age):
    response.set_cookie(
        name,
        token,
        max_age=max_age,
        path=settings.AUTH_COOKIE_PATH,
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            set_token_cookie(response, "access", response.data["access"], settings.AUTH_COOKIE_ACCESS_MAX_AGE)
            set_token_cookie(response, "refresh", response.data["refresh"], settings.AUTH_COOKIE_REFRESH_MAX_AGE)
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def get_serializer(self, *args, **kwargs):
        data = kwargs.get("data")
        cookie = self.request.COOKIES.get("refresh")
        if data is not None and not data.get("refresh") and cookie:
            kwargs["data"] = {"refresh": cookie}
        return super().get_serializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            set_token_cookie(response, "access", response.data["access"], settings.AUTH_COOKIE_ACCESS_MAX_AGE)
            if response.data.get("refresh"):
                set_token_cookie(response, "refresh", response.data["refresh"], settings.AUTH_COOKIE_REFRESH_MAX_AGE)
        return response


class CustomTokenVerifyView(TokenVerifyView):
    def get_serializer(self, *args, **kwargs):
        data = kwargs.get("data")
        cookie = self.request.COOKIES.get("access")
        if data is not None and not data.get("token") and cookie:
            kwargs["data"] = {"token": cookie}
        return super().get_serializer(*args, **kwargs)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        token = request.data.get("refresh") or request.COOKIES.get("refresh")
        if isinstance(token, str):
            try:
                RefreshToken(token).blacklist()
            except TokenError:
                # Logging out twice must still clear cookies.
                pass

        response = Response(status=status.HTTP_204_NO_CONTENT)
        for name in ("access", "refresh"):
            response.delete_cookie(
                name, path=settings.AUTH_COOKIE_PATH, samesite=settings.AUTH_COOKIE_SAMESITE
            )
        return response
