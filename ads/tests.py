from datetime import timedelta
from uuid import uuid4

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import AdClick, AdImpression, Advertisement, Advertiser, Campaign


class AdEventTests(APITestCase):
    def setUp(self):
        now = timezone.now()
        campaign = Campaign.objects.create(
            advertiser=Advertiser.objects.create(name="Test advertiser"),
            name="Test campaign",
            status="ACTIVE",
            start_at=now - timedelta(hours=1),
            end_at=now + timedelta(hours=1),
        )
        self.ad = Advertisement.objects.create(campaign=campaign, title="Test ad")
        self.session = {"session_id": str(uuid4())}

    def test_impression_progress_updates_one_event(self):
        url = reverse("ad-impression", args=[self.ad.id])
        original = self.client.post(url, self.session, format="json")
        self.assertEqual(original.status_code, 201)
        updated = self.client.post(
            url,
            {**self.session, "watched_seconds": 15, "watched_percentage": 100, "completed": True},
            format="json",
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(original.data["impression_id"], updated.data["impression_id"])
        self.assertEqual(AdImpression.objects.count(), 1)
        self.assertTrue(AdImpression.objects.get().completed)

    def test_click_retries_do_not_add_an_event(self):
        url = reverse("ad-click", args=[self.ad.id])
        original = self.client.post(url, self.session, format="json")
        retry = self.client.post(url, self.session, format="json")
        self.assertEqual(original.status_code, 201)
        self.assertEqual(retry.status_code, 200)
        self.assertEqual(original.data["click_id"], retry.data["click_id"])
        self.assertEqual(AdClick.objects.count(), 1)

    def test_paused_campaign_ignores_impressions(self):
        Campaign.objects.filter(pk=self.ad.campaign_id).update(status="PAUSED")
        url = reverse("ad-impression", args=[self.ad.id])
        response = self.client.post(url, self.session, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(AdImpression.objects.exists())

    def test_anonymous_cannot_create_campaign(self):
        response = self.client.post(reverse("campaign-list-create"), {}, format="json")
        self.assertIn(response.status_code, (401, 403))
