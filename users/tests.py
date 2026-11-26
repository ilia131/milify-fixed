from unittest.mock import Mock, patch
from django.core import mail

from django.urls import Resolver404, resolve
from django.test import override_settings
from rest_framework.test import APITestCase

from accounts.models import UserListener
from artists.models import Artist


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class RegistrationTests(APITestCase):
    payload = {
        "email": "NewListener@example.com",
        "username": "newlistener",
        "first_name": "New",
        "last_name": "Listener",
        "password": "long-random-87!secret",
        "re_password": "long-random-87!secret",
    }

    def test_registration_login_and_refresh_without_email_activation(self):
        response = self.client.post("/api/users/", self.payload, format="json")
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertNotIn("password", response.data)
        self.assertNotIn("re_password", response.data)

        user = UserListener.objects.get(email=self.payload["email"].lower())
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password(self.payload["password"]))

        response = self.client.post(
            "/api/jwt/create/",
            {"email": user.email, "password": self.payload["password"]},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        access = response.data["access"]
        profile = self.client.get("/api/users/me/", HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(profile.status_code, 200, profile.data)
        self.assertEqual(profile.data["email"], user.email)
        refresh = self.client.post(
            "/api/jwt/refresh/", {"refresh": response.data["refresh"]}, format="json"
        )
        self.assertEqual(refresh.status_code, 200, refresh.data)
        self.assertIn("access", refresh.data)
        rotated_refresh = refresh.data["refresh"]
        self.assertEqual(refresh.cookies["refresh"].value, rotated_refresh)
        rejected = self.client.post(
            "/api/jwt/refresh/", {"refresh": response.data["refresh"]}, format="json"
        )
        self.assertEqual(rejected.status_code, 401)
        logout = self.client.post("/api/logout/", {"refresh": rotated_refresh}, format="json")
        self.assertEqual(logout.status_code, 204)
        rejected = self.client.post(
            "/api/jwt/refresh/", {"refresh": rotated_refresh}, format="json"
        )
        self.assertEqual(rejected.status_code, 401)


    def test_rejects_weak_password(self):
        response = self.client.post(
            "/api/users/",
            {**self.payload, "password": "12345678", "re_password": "12345678"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)
        self.assertFalse(UserListener.objects.exists())

    def test_activation_routes_removed_and_password_reset_retained(self):
        for prefix in ("/api", "/users"):
            for action in ("activation", "resend_activation"):
                with self.subTest(prefix=prefix, action=action), self.assertRaises(Resolver404):
                    resolve(f"{prefix}/users/{action}/")
            self.assertEqual(
                resolve(f"{prefix}/users/reset_password/").url_name, "userlistener-reset-password"
            )

    def test_google_login_respects_disabled_account(self):
        user = UserListener.objects.create_user(
            email="disabled@example.com", username="disabled", is_active=False
        )
        verification = Mock(status_code=200)
        verification.json.return_value = {
            "aud": "test-client",
            "iss": "https://accounts.google.com",
            "email": user.email,
            "email_verified": True,
        }
        with self.settings(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="test-client"):
            with patch("users.views.requests.get", return_value=verification):
                response = self.client.post(
                    "/api/google/login/", {"id_token": "test-token"}, format="json"
                )
        self.assertEqual(response.status_code, 401)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_new_google_listener_can_save_favorite_artists(self):

        creator = UserListener.objects.create_user(
            email="artist@example.com", username="artist"
        )
        artist = Artist.objects.create(user=creator, artistname="test-artist")
        verification = Mock(status_code=200)
        verification.json.return_value = {
            "aud": "test-client",
            "iss": "accounts.google.com",
            "email": "google-listener@example.com",
            "email_verified": True,
        }
        with self.settings(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="test-client"):
            with patch("users.views.requests.get", return_value=verification):
                login = self.client.post(
                    "/api/google/login/", {"id_token": "test-token"}, format="json"
                )

        self.assertEqual(login.status_code, 200, login.data)
        self.assertTrue(login.data["created"])
        profile = self.client.post(
            "/api/google/complete-profile/",
            {"favorite_artists": [artist.artistname]},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}",
        )
        self.assertEqual(profile.status_code, 200, profile.data)
        user = UserListener.objects.get(email="google-listener@example.com")
        self.assertTrue(user.is_active)
        self.assertEqual(list(user.favorite_artists.all()), [artist])
