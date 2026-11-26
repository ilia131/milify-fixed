from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import UserListener
from subscriptions.models import Payment, SubscriptionPlan, Wallet, WalletTransaction


class SubscriptionPurchaseTests(APITestCase):
    def setUp(self):
        user = UserListener.objects.create_user(
            email="buyer@example.com", username="buyer"
        )
        self.wallet, _ = Wallet.objects.get_or_create(user=user)
        self.wallet.balance = Decimal("100")
        self.wallet.save(update_fields=["balance"])
        self.client.force_authenticate(user)
        self.url = reverse("purchase-subscription")
        self.plan = SubscriptionPlan.objects.create(name="Monthly", price=30)

    def test_repeat_request_does_not_charge_twice(self):
        payload = {"plan_id": str(self.plan.pk)}
        purchase = self.client.post(self.url, payload, format="json")
        self.assertEqual(purchase.status_code, 201, purchase.data)
        retry = self.client.post(self.url, payload, format="json")
        self.assertEqual(retry.status_code, 400)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("70"))
        self.assertEqual(Payment.objects.filter(status="SUCCESS").count(), 1)
        self.assertEqual(WalletTransaction.objects.filter(wallet=self.wallet).count(), 1)

    def test_invalid_plan_id_returns_bad_request(self):
        response = self.client.post(self.url, {"plan_id": "invalid"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Payment.objects.exists())
