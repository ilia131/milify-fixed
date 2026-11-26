import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone



class Wallet(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.user} - {self.balance}"
    

class WalletTransaction(models.Model):

    TYPE_CHOICES = [
        (
            "DEPOSIT",
            "Deposit"
        ),
        (
            "SUBSCRIPTION_PURCHASE",
            "Subscription Purchase"
        ),
        (
            "BEAT_PURCHASE",
            "Beat Purchase"
        ),
        (
            "BEAT_REVENUE",
            "Beat Revenue"
        ),
        (
            "REFUND",
            "Refund"
        ),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    transaction_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):

        return (
            f"{self.wallet.user} - "
            f"{self.amount} - "
            f"{self.transaction_type}"
        )

class SubscriptionPlan(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    duration_days = models.PositiveIntegerField(
        default=30
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class Subscription(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACTIVE", "Active"),
        ("EXPIRED", "Expired"),
        ("CANCELLED", "Cancelled"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def is_active_subscription(self):

        return (
            self.status == "ACTIVE"
            and self.expires_at is not None
            and self.expires_at > timezone.now()
        )

    def __str__(self):
        return f"{self.user} - {self.plan}"
    
    

class Payment(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    # اشتراک عمومی پلتفرم
    subscription = models.ForeignKey(
        "Subscription",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments"
    )

    # اشتراک آرتیست
    artist_subscription = models.ForeignKey(
        "ArtistSubscription",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    authority = models.CharField(
        max_length=255,
        blank=True,
        db_index=True
    )

    ref_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user} - {self.amount}"
    





class ArtistSubscriptionPlan(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    artist = models.OneToOneField(
        "artists.Artist",
        on_delete=models.CASCADE,
        related_name="subscription_plan",
    )

    name = models.CharField(
        max_length=100,
        default="اشتراک ماهانه",
    )

    description = models.TextField(
        blank=True,
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
    )

    duration_days = models.PositiveIntegerField(
        default=30,
    )

    is_active = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.artist.artistname} - {self.name}"
    
    
class ArtistSubscription(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACTIVE", "Active"),
        ("EXPIRED", "Expired"),
        ("CANCELLED", "Cancelled"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="artist_subscriptions",
    )

    artist = models.ForeignKey(
        "artists.Artist",
        on_delete=models.CASCADE,
        related_name="subscribers",
    )

    plan = models.ForeignKey(
        ArtistSubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @property
    def is_active_subscription(self):
        return (
            self.status == "ACTIVE"
            and self.expires_at is not None
            and self.expires_at > timezone.now()
        )

    def __str__(self):
        return (
            f"{self.user} -> "
            f"{self.artist.artistname}"
        )
        

class ArtistSubscriptionTrack(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    artist = models.ForeignKey(
        "artists.Artist",
        on_delete=models.CASCADE,
        related_name="subscription_tracks",
    )

    song = models.ForeignKey(
        "music.Songs",
        on_delete=models.CASCADE,
        related_name="artist_subscription_access",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["artist", "song"],
                name="unique_artist_subscription_song",
            )
        ]

    def __str__(self):
        return f"{self.artist.artistname} - {self.song.title}"
    

class PlatformRevenue(models.Model):

    REVENUE_TYPES = [
        (
            "BEAT_SALE",
            "Beat Sale",
        ),
        (
            "SUBSCRIPTION",
            "Subscription",
        ),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    revenue_type = models.CharField(
        max_length=30,
        choices=REVENUE_TYPES,
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    purchase = models.ForeignKey(
        "music_producer.BeatPurchase",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="platform_revenues",
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.revenue_type} - "
            f"{self.amount}"
        )