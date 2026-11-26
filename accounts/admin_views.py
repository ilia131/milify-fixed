# users/admin_views.py

from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from accounts.admin_pagination import  AdminUserPagination
from accounts.models import UserListener
from accounts.admin_serializers import (
    AdminUserSerializer,
    AdminUserCreateSerializer,
)
from accounts.admin_serializers import (
    AdminUserSerializer,
    AdminUserCreateSerializer,
)

from django.shortcuts import get_object_or_404

from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken


class AdminLoginView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {
                    "detail": "Email and password are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            request=request,
            username=email,
            password=password
        )

        if user is None:
            return Response(
                {
                    "detail": "Invalid email or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {
                    "detail": "This account is inactive."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # مهم‌ترین قسمت
        if not user.is_staff and not user.is_superuser:
            return Response(
                {
                    "detail": "You do not have permission to access the admin panel."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK
        )
class AdminUserListView(generics.ListAPIView):

    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]

    pagination_class = AdminUserPagination

    def get_queryset(self):

        queryset = (
            UserListener.objects
            .prefetch_related(
                "favorite_genres",
                "favorite_artists",
                "subscriptions",
            )
            .order_by("-created_at")
        )

        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        is_artist = self.request.query_params.get("is_artist")

        if is_artist in ["true", "false"]:
            queryset = queryset.filter(
                is_artist=is_artist == "true"
            )

        is_active = self.request.query_params.get("is_active")

        if is_active in ["true", "false"]:
            queryset = queryset.filter(
                is_active=is_active == "true"
            )

        return queryset

class AdminUserDetailView(generics.RetrieveAPIView):

    queryset = UserListener.objects.all()

    serializer_class = AdminUserSerializer

    permission_classes = [
        IsAdminUser
    ]

    lookup_field = "id"


class AdminUserUpdateView(APIView):

    permission_classes = [
        IsAdminUser
    ]

    def put(self, request, id):

        user = get_object_or_404(
            UserListener,
            id=id
        )

        serializer = AdminUserSerializer(
            user,
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )



class AdminUserDetailView(generics.RetrieveAPIView):

    queryset = UserListener.objects.all()

    serializer_class = AdminUserSerializer

    permission_classes = [
        IsAdminUser
    ]

    lookup_field = "id"
    
    

class AdminUserToggleActiveView(APIView):

    permission_classes = [
        IsAdminUser
    ]

    def patch(self, request, id):

        try:
            user = UserListener.objects.get(id=id)

        except UserListener.DoesNotExist:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        user.is_active = not user.is_active
        user.save(
            update_fields=["is_active"]
        )

        return Response({
            "id": user.id,
            "is_active": user.is_active
        })
        
        
        

class AdminUserCreateView(APIView):

    permission_classes = [
        IsAdminUser
    ]

    def post(self, request):

        serializer = AdminUserCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        return Response(
            AdminUserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
        
        

class AdminUserPasswordView(APIView):

    permission_classes = [
        IsAdminUser
    ]

    def patch(self, request, id):

        user = get_object_or_404(
            UserListener,
            id=id
        )

        password = request.data.get("password")

        if not password:
            return Response(
                {
                    "detail": "Password is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 8:
            return Response(
                {
                    "detail": "Password must be at least 8 characters."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(password)
        user.save(update_fields=["password"])

        return Response({
            "detail": "Password changed successfully."
        })
        
        
        
        

class AdminUserDeleteView(APIView):

    permission_classes = [
        IsAdminUser
    ]

    def delete(self, request, id):

        user = get_object_or_404(
            UserListener,
            id=id
        )

        # جلوگیری از حذف خود ادمین
        if user.id == request.user.id:
            return Response(
                {
                    "detail": "You cannot delete your own account."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.delete()

        return Response(
            {
                "detail": "User deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )
        
        
