import uuid

from django.conf import settings
from django.db import models


class Advertiser(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=200
    )

    website = models.URLField(
        blank=True
    )

    logo = models.ImageField(
        upload_to="ads/advertisers/",
        blank=True,
        null=True
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


class Campaign(models.Model):

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("ACTIVE", "Active"),
        ("PAUSED", "Paused"),
        ("COMPLETED", "Completed"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    advertiser = models.ForeignKey(
        Advertiser,
        on_delete=models.CASCADE,
        related_name="campaigns"
    )

    name = models.CharField(
        max_length=200
    )

    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    spent = models.DecimalField(
        max_digits=17,
        decimal_places=7,
        default=0
    )

    start_at = models.DateTimeField()

    end_at = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def remaining_budget(self):
        return max(
            self.budget - self.spent,
            0
        )

    def __str__(self):
        return self.name


class Advertisement(models.Model):

    AD_TYPE_CHOICES = [
        ("IMAGE", "Image"),
        ("VIDEO", "Video"),
    ]

    PRICING_MODEL_CHOICES = [
        ("CPM", "CPM"),
        ("CPC", "CPC"),
        ("CPV", "CPV"),
    ]

    PLACEMENT_CHOICES = [
        ("HOME", "Home"),
        ("SEARCH", "Search"),
        ("PLAYER", "Player"),
        ("ARTIST", "Artist"),
        ("ALBUM", "Album"),
        ("DISCOVERY", "Discovery"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="ads"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    ad_type = models.CharField(
        max_length=10,
        choices=AD_TYPE_CHOICES,
        default="IMAGE"
    )

    image = models.ImageField(
        upload_to="ads/images/",
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to="ads/videos/",
        blank=True,
        null=True
    )

    target_url = models.URLField()

    placement = models.CharField(
        max_length=20,
        choices=PLACEMENT_CHOICES,
        default="HOME"
    )

    pricing_model = models.CharField(
        max_length=10,
        choices=PRICING_MODEL_CHOICES,
        default="CPM"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0
    )

    duration = models.PositiveIntegerField(
        default=0,
        help_text="Video duration in seconds"
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
        return self.title


class AdImpression(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    ad = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name="impressions"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ad_impressions"
    )

    session_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True
    )

    watched_seconds = models.PositiveIntegerField(
        default=0
    )

    watched_percentage = models.PositiveSmallIntegerField(
        default=0
    )

    completed = models.BooleanField(
        default=False
    )

    charged_amount = models.DecimalField(max_digits=17, decimal_places=7, default=0)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["ad", "created_at"]
            ),
            models.Index(
                fields=["user", "created_at"]
            ),
        ]


class AdClick(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    ad = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name="clicks"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ad_clicks"
    )

    session_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True
    )

    charged_amount = models.DecimalField(max_digits=17, decimal_places=7, default=0)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["ad", "created_at"]
            ),
            models.Index(
                fields=["user", "created_at"]
            ),
        ]
