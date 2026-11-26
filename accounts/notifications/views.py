# users/admin_views.py

from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAdminUser , IsAuthenticated
from rest_framework import status

 
from django.shortcuts import get_object_or_404
from .serializers import UserNotificationSerializer , UserNotification , PushSubscription , PushSubscriptionSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken


class NotificationListView(generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserNotification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        notification = get_object_or_404(
            UserNotification,
            id=id,
            user=request.user,
        )

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response(
            {
                "detail": "Notification marked as read."
            },
            status=status.HTTP_200_OK,
        )


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        UserNotification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(is_read=True)

        return Response(
            {
                "detail": "All notifications marked as read."
            },
            status=status.HTTP_200_OK,
        )


class NotificationDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        notification = generics.get_object_or_404(
            UserNotification,
            id=id,
            user=request.user,
        )

        notification.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class PushSubscriptionCreateView(generics.CreateAPIView):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [IsAuthenticated]


class PushSubscriptionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        subscription = generics.get_object_or_404(
            PushSubscription,
            id=id,
            user=request.user,
        )

        subscription.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )