from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from users.models import UserAccountManager
from music.models import Genre
import uuid

class UserListener(
    AbstractBaseUser,
    PermissionsMixin
):

    email = models.EmailField(
        unique=True,
        max_length=255
    )
    
    username = models.CharField(
        max_length=120,
        unique=True
    )

    first_name = models.CharField(
        max_length=120,
        blank=True
    )

    last_name = models.CharField(
        max_length=120,
        blank=True
    )

    profile_pic = models.ImageField(
        upload_to="users/",
        null=True,
        blank=True
    )

    is_artist = models.BooleanField(
        default=False
    )

    favorite_genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name="listeners"
    )

    favorite_artists = models.ManyToManyField(
        "artists.Artist",
        blank=True,
        related_name="fans"
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    objects = UserAccountManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]

    def __str__(self):
        return self.username

    def get_image(self):
        if self.profile_pic:
            return (
                "http://127.0.0.1:8000/"
                + self.profile_pic.url
            )

        return ""

    @property
    def has_active_subscription(self):
        return self.subscriptions.filter(
            status="ACTIVE",
            expires_at__gt=timezone.now()
        ).exists()
        
        
        

class UserNotification(models.Model):
    user = models.ForeignKey(
        UserListener,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.CharField(
        max_length=500,
        blank=True,
        default=""
    )
    notification_type = models.CharField(
        max_length=50,
        default="general"
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        
        
        

class PushSubscription(models.Model):
    user = models.ForeignKey(
        UserListener,
        on_delete=models.CASCADE,
        related_name="push_subscriptions"
    )

    endpoint = models.TextField(unique=True)
    p256dh = models.TextField()
    auth = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    
    
    

class SupportRequest(models.Model):

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In Progress"),
        ("ANSWERED", "Answered"),
        ("CLOSED", "Closed"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        UserListener,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_requests"
    )

    email = models.EmailField(
        blank=True,
        default=""
    )

    subject = models.CharField(
        max_length=255
    )

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="OPEN"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject