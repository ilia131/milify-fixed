from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import UserListener
from subscriptions.models import PlatformRevenue, Wallet, WalletTransaction
from .models import Beat, BeatLicense, BeatPurchase, ProducerProfile


class BeatPurchaseTests(APITestCase):
    def setUp(self):
        self.seller = UserListener.objects.create_user(email="seller@example.com", username="seller")
        self.buyer = UserListener.objects.create_user(email="buyer@example.com", username="buyer")
        self.producer = ProducerProfile.objects.create(user=self.seller, producer_name="Studio")
        self.beat = Beat.objects.create(
            producer=self.producer, title="Studio track", slug="studio-track", price=Decimal("12.37"),
            preview_audio="beats/previews/test.mp3",
        )
        self.license = BeatLicense.objects.create(
            beat=self.beat, license_type="BASIC", name="Basic", price=Decimal("12.37"),
            audio_file="beats/files/test.mp3",
        )
        Wallet.objects.update_or_create(user=self.buyer, defaults={"balance": Decimal("20.00")})
        self.client.force_authenticate(self.buyer)
        self.url = reverse("buy-beat", args=[self.beat.pk])

    def test_purchase_keeps_fractional_balance_and_creates_one_ledger_entry_per_party(self):
        response = self.client.post(self.url, {"license_id": self.license.pk}, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        repeated = self.client.post(self.url, {"license_id": self.license.pk}, format="json")
        self.assertEqual(repeated.status_code, 400)
        self.assertEqual(BeatPurchase.objects.count(), 1)
        self.assertEqual(Wallet.objects.get(user=self.buyer).balance, Decimal("7.63"))
        self.assertEqual(Wallet.objects.get(user=self.seller).balance, Decimal("9.90"))
        self.assertEqual(PlatformRevenue.objects.get().amount, Decimal("2.47"))
        self.assertEqual(WalletTransaction.objects.count(), 2)

    def test_invalid_license_returns_a_client_error_without_creating_a_purchase(self):
        response = self.client.post(self.url, {"license_id": "invalid"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(BeatPurchase.objects.exists())
