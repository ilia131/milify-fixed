import os

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from accounts.models import UserListener


class Command(BaseCommand):
    help = "Create the initial admin user from environment variables"

    def handle(self, *args, **options):
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        username = os.getenv("ADMIN_USERNAME")
        first_name = os.getenv("ADMIN_FIRST_NAME", "Admin")
        last_name = os.getenv("ADMIN_LAST_NAME", "User")

        if not email or not password or not username:
            self.stdout.write(
                self.style.ERROR(
                    "ADMIN_EMAIL, ADMIN_PASSWORD and ADMIN_USERNAME "
                    "must be set."
                )
            )
            return

        if UserListener.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Admin with email {email} already exists."
                )
            )
            return

        if UserListener.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Username {username} already exists."
                )
            )
            return

        try:
            user = UserListener.objects.create_superuser(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser created successfully: {user.email}"
                )
            )

        except IntegrityError as exc:
            self.stdout.write(
                self.style.ERROR(
                    f"Could not create superuser: {exc}"
                )
            )