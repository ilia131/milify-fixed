from unittest.mock import Mock, patch
from django.core import mail

from django.urls import Resolver404, resolve
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

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
        self.assertTrue(login.cookies["access"]["httponly"])
        self.assertTrue(login.cookies["refresh"]["httponly"])
        with self.settings(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="test-client"):
            with patch("users.views.requests.get", return_value=verification):
                repeat = self.client.post(
                    "/api/google/login/", {"id_token": "test-token"}, format="json"
                )
        self.assertEqual(repeat.status_code, 200)
        self.assertFalse(repeat.data["created"])
        self.assertEqual(repeat.data["user"]["id"], login.data["user"]["id"])

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

    def test_cookie_authentication_requires_csrf_on_writes(self):
        from rest_framework_simplejwt.tokens import RefreshToken

        listener = UserListener.objects.create_user(
            email="cookie@example.com", username="cookie-listener",
        )
        access = str(RefreshToken.for_user(listener).access_token)
        client = APIClient(enforce_csrf_checks=True)
        client.cookies["access"] = access
        path = "/api/google/complete-profile/"
        self.assertEqual(client.post(path, {"favorite_artists": []}, format="json").status_code, 403)
        self.assertEqual(client.post(
            path, {"favorite_artists": []}, format="json", HTTP_AUTHORIZATION=f"Bearer {access}"
        ).status_code, 200)


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    FRONTEND_URL="https://frontend.example.com",
)
class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = UserListener.objects.create_user(
            email="reset@example.com", username="reset-test", password="Old-long-safe!42"
        )

    def test_reset_email_token_and_single_use(self):
        from re import search

        requested = self.client.post(
            "/api/users/reset_password/", {"email": self.user.email}, format="json"
        )
        self.assertEqual(requested.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)
        link = search(r"https://frontend\.example\.com/reset-password/([^/\s]+)/([\w-]+)", mail.outbox[0].body)
        self.assertIsNotNone(link)
        payload = {
            "uid": link[1], "token": link[2],
            "new_password": "New-long-safe!43", "re_new_password": "New-long-safe!43",
        }
        confirmed = self.client.post("/api/users/reset_password_confirm/", payload, format="json")
        self.assertEqual(confirmed.status_code, 204, confirmed.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload["new_password"]))
        replayed = self.client.post("/api/users/reset_password_confirm/", payload, format="json")
        self.assertEqual(replayed.status_code, 400)

    @override_settings(PASSWORD_RESET_TIMEOUT=1)
    def test_expired_token_is_rejected(self):
        from datetime import datetime, timedelta
        from django.contrib.auth.tokens import default_token_generator
        from djoser.utils import encode_uid

        with patch.object(default_token_generator, "_now", return_value=datetime.now() - timedelta(seconds=10)):
            token = default_token_generator.make_token(self.user)
        response = self.client.post(
            "/api/users/reset_password_confirm/",
            {"uid": encode_uid(self.user.pk), "token": token,
             "new_password": "New-long-safe!43", "re_new_password": "New-long-safe!43"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_smtp_failure_and_unknown_email_return_same_response(self):
        with patch("djoser.email.BaseEmailMessage.send", side_effect=ConnectionError):
            known = self.client.post(
                "/api/users/reset_password/", {"email": self.user.email}, format="json"
            )
            unknown = self.client.post(
                "/api/users/reset_password/", {"email": "unknown@example.com"}, format="json"
            )
        self.assertEqual(known.status_code, 204)
        self.assertEqual(unknown.status_code, known.status_code)
        self.assertEqual(known.content, unknown.content)
