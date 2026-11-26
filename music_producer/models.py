import uuid

from django.conf import settings
from django.db import models


class ProducerProfile(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="producer_profile"
    )

    producer_name = models.CharField(
        max_length=150,
        unique=True
    )

    bio = models.TextField(
        blank=True
    )

    profile_pic = models.ImageField(
        upload_to="producers/profile/",
        null=True,
        blank=True
    )

    cover_image = models.ImageField(
        upload_to="producers/covers/",
        null=True,
        blank=True
    )

    instagram = models.URLField(
        blank=True
    )

    youtube = models.URLField(
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    total_sales = models.PositiveIntegerField(
        default=0
    )

    total_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.producer_name
    
    
    


class Beat(models.Model):

    GENRE_CHOICES = [
        ("TRAP", "Trap"),
        ("HIPHOP", "Hip Hop"),
        ("DRILL", "Drill"),
        ("RNB", "R&B"),
        ("POP", "Pop"),
        ("LOFI", "Lo-Fi"),
        ("OTHER", "Other"),
    ]

    producer = models.ForeignKey(
        ProducerProfile,
        on_delete=models.CASCADE,
        related_name="beats"
    )

    title = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        max_length=255,
        unique=True
    )

    genre = models.CharField(
        max_length=30,
        choices=GENRE_CHOICES,
        default="OTHER"
    )

    bpm = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    key = models.CharField(
        max_length=20,
        blank=True
    )

    cover = models.ImageField(
        upload_to="beats/covers/",
        null=True,
        blank=True
    )

    preview_audio = models.FileField(
        upload_to="beats/previews/"
    )

    description = models.TextField(
        blank=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    is_active = models.BooleanField(
        default=True
    )

    is_featured = models.BooleanField(
        default=False
    )

    plays = models.PositiveBigIntegerField(
        default=0
    )

    sales = models.PositiveIntegerField(
        default=0
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
        return self.title
    
    
    

class BeatLicense(models.Model):

    LICENSE_TYPES = [
        ("BASIC", "Basic"),
        ("PREMIUM", "Premium"),
        ("EXCLUSIVE", "Exclusive"),
    ]

    beat = models.ForeignKey(
        Beat,
        on_delete=models.CASCADE,
        related_name="licenses"
    )

    license_type = models.CharField(
        max_length=20,
        choices=LICENSE_TYPES
    )

    name = models.CharField(
        max_length=100
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    audio_file = models.FileField(
        upload_to="beats/files/"
    )

    commercial_use = models.BooleanField(
        default=False
    )

    stems_included = models.BooleanField(
        default=False
    )

    exclusive = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.beat.title} - {self.name}"
    
    
    

class BeatPurchase(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("REFUNDED", "Refunded"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="beat_purchases",
    )

    beat = models.ForeignKey(
            Beat,
            on_delete=models.PROTECT,
            related_name="purchases",
        )

    license = models.ForeignKey(
            BeatLicense,
            on_delete=models.PROTECT,
            related_name="purchases",
            null=True,
            blank=True,
        )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    platform_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    producer_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="COMPLETED",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "beat",
                    "license",
                ],
                name="unique_user_beat_license_purchase",
            )
        ]

    def __str__(self):
        return (
            f"{self.user} -> "
            f"{self.beat.title}"
        )