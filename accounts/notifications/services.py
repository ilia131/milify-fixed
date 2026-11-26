import json

from django.conf import settings
from django.contrib.auth import get_user_model
from pywebpush import webpush, WebPushException

from accounts.models import UserNotification, PushSubscription


User = get_user_model()


class NotificationService:

    @staticmethod
    def send_to_user(
        user,
        title,
        message,
        notification_type="general",
        url="/",
    ):
        # In-App Notification
        notification = UserNotification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            url=url,
        )

        # Web Push
        subscriptions = PushSubscription.objects.filter(
            user=user
        )

        payload = json.dumps({
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "url": url,
        })

        for subscription in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {
                            "p256dh": subscription.p256dh,
                            "auth": subscription.auth,
                        },
                    },
                    data=payload,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims=settings.VAPID_CLAIMS,
                )

            except WebPushException as exc:
                status_code = getattr(
                    exc.response,
                    "status_code",
                    None,
                )

                if status_code in [404, 410]:
                    subscription.delete()

        return notification

    @staticmethod
    def send_to_all_users(
        title,
        message,
        notification_type="general",
        url="/",
    ):
        users = User.objects.filter(
            is_active=True
        )

        notifications = [
            UserNotification(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                url=url,
            )
            for user in users
        ]

        UserNotification.objects.bulk_create(
            notifications,
            batch_size=500,
        )

        # Web Push
        for user in users.iterator():

            subscriptions = PushSubscription.objects.filter(
                user=user
            )

            payload = json.dumps({
                "title": title,
                "message": message,
                "notification_type": notification_type,
                "url": url,
            })

            for subscription in subscriptions:
                try:
                    webpush(
                        subscription_info={
                            "endpoint": subscription.endpoint,
                            "keys": {
                                "p256dh": subscription.p256dh,
                                "auth": subscription.auth,
                            },
                        },
                        data=payload,
                        vapid_private_key=settings.VAPID_PRIVATE_KEY,
                        vapid_claims=settings.VAPID_CLAIMS,
                    )

                except WebPushException as exc:
                    status_code = getattr(
                        exc.response,
                        "status_code",
                        None,
                    )

                    if status_code in [404, 410]:
                        subscription.delete()