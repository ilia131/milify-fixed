from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from django.db import connections
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase, APITransactionTestCase

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

    def test_cpm_charges_exact_fraction_once(self):

        self.ad.pricing_model = "CPM"
        self.ad.price = Decimal("0.0001")
        self.ad.save(update_fields=["pricing_model", "price"])
        Campaign.objects.filter(pk=self.ad.campaign_id).update(budget=Decimal("1.00"))
        url = reverse("ad-impression", args=[self.ad.id])
        self.assertEqual(self.client.post(url, self.session, format="json").status_code, 201)
        self.assertEqual(self.client.post(url, self.session, format="json").status_code, 200)
        self.assertEqual(AdImpression.objects.get().charged_amount, Decimal("0.0000001"))
        self.assertEqual(Campaign.objects.get(pk=self.ad.campaign_id).spent, Decimal("0.0000001"))

    def test_cpc_enforces_budget_without_recording_unfunded_click(self):

        self.ad.pricing_model = "CPC"
        self.ad.price = Decimal("0.75")
        self.ad.save(update_fields=["pricing_model", "price"])
        Campaign.objects.filter(pk=self.ad.campaign_id).update(budget=Decimal("1.00"))
        url = reverse("ad-click", args=[self.ad.id])
        self.assertEqual(self.client.post(url, self.session, format="json").status_code, 201)
        self.assertEqual(self.client.post(url, self.session, format="json").status_code, 200)
        response = self.client.post(url, {"session_id": str(uuid4())}, format="json")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(AdClick.objects.count(), 1)
        self.assertEqual(Campaign.objects.get(pk=self.ad.campaign_id).spent, Decimal("0.75"))

    def test_cpv_charges_only_completed_video_and_does_not_charge_twice(self):

        self.ad.pricing_model = "CPV"
        self.ad.ad_type = "VIDEO"
        self.ad.duration = 15
        self.ad.price = Decimal("1")
        self.ad.save(update_fields=["pricing_model", "ad_type", "duration", "price"])
        Campaign.objects.filter(pk=self.ad.campaign_id).update(budget=Decimal("2.00"))
        url = reverse("ad-impression", args=[self.ad.id])
        incomplete = {**self.session, "watched_seconds": 10, "watched_percentage": 80, "completed": True}
        response = self.client.post(url, incomplete, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Campaign.objects.get(pk=self.ad.campaign_id).spent, Decimal("0"))

        complete = {**incomplete, "watched_seconds": 15, "watched_percentage": 100}
        self.assertEqual(self.client.post(url, complete, format="json").status_code, 200)
        self.assertEqual(self.client.post(url, complete, format="json").status_code, 200)
        self.assertEqual(AdImpression.objects.get().charged_amount, Decimal("1"))
        self.assertEqual(Campaign.objects.get(pk=self.ad.campaign_id).spent, Decimal("1"))


class CampaignRaceTests(APITransactionTestCase):
    def test_concurrent_billable_clicks_cannot_overspend_shared_campaign(self):
        now = timezone.now()
        campaign = Campaign.objects.create(
            advertiser=Advertiser.objects.create(name="Concurrent advertiser"),
            name="One click budget", status="ACTIVE", budget=Decimal("1.00"),
            start_at=now - timedelta(hours=1), end_at=now + timedelta(hours=1),
        )
        ads = [
            Advertisement.objects.create(campaign=campaign, title=title, pricing_model="CPC", price=1)
            for title in ("First", "Second")
        ]
        start = Barrier(2)

        def click(ad):
            try:
                start.wait(timeout=5)
                client = APIClient()
                response = client.post(
                    reverse("ad-click", args=[ad.id]), {"session_id": str(uuid4())}, format="json"
                )
                return response.status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = sorted(executor.map(click, ads))
        self.assertEqual(statuses, [201, 409])
        campaign.refresh_from_db()
        self.assertEqual(campaign.spent, Decimal("1.00"))
        self.assertEqual(AdClick.objects.count(), 1)
