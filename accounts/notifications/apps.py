from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts.notifications"

    def ready(self):
        import accounts.notifications.signals