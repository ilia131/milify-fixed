from datetime import timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import UserListener
from artists.models import Artist
from music.models import Songs, TrackArtist
from recentlyplayed.models import RecentlyPlayed
from subscriptions.models import (
    ArtistSubscription,
    ArtistSubscriptionPlan,
    ArtistSubscriptionTrack,
)


class PlaybackTests(APITestCase):
    def setUp(self):
        self.listener = UserListener.objects.create_user(
            email="listener@example.com", username="listener"
        )
        self.song = Songs.objects.create(title="Test track", duration=100)

    def test_listen_counts_once_at_thirty_seconds(self):
        self.client.force_authenticate(self.listener)
        url = reverse("song-listen", args=[self.song.unique_id])
        session_id = str(uuid4())
        for seconds, counted in ((29, False), (30, True), (30, False), (37, False)):
            with self.subTest(seconds=seconds):
                response = self.client.post(
                    url, {"seconds": seconds, "session_id": session_id}, format="json"
                )
                self.assertEqual(response.status_code, 200, response.data)
                self.assertEqual(response.data["play_counted"], counted)

        self.song.refresh_from_db()
        self.assertEqual(self.song.total_listen_time, 37)
        self.assertEqual(self.song.play_count, 1)
        self.assertTrue(RecentlyPlayed.objects.filter(user=self.listener, song=self.song).exists())

    def test_subscription_gates_both_audio_fields_and_listening(self):
        creator = UserListener.objects.create_user(
            email="creator@example.com", username="creator"
        )
        artist = Artist.objects.create(user=creator, artistname="Creator")
        TrackArtist.objects.create(track=self.song, artist=artist, role="main")
        ArtistSubscriptionTrack.objects.create(song=self.song, artist=artist, status="APPROVED")
        self.song.track = "music/test.mp3"
        self.song.save(update_fields=["track"])

        url = reverse("song-player", args=[self.song.unique_id])
        anonymous = self.client.get(url)
        self.assertEqual(anonymous.status_code, 200)
        self.assertIsNone(anonymous.data["track"])
        self.assertIsNone(anonymous.data["track_url"])

        self.client.force_authenticate(self.listener)
        listen = self.client.post(
            reverse("song-listen", args=[self.song.unique_id]),
            {"seconds": 30, "session_id": str(uuid4())},
            format="json",
        )
        self.assertEqual(listen.status_code, 403)

        now = timezone.now()
        plan = ArtistSubscriptionPlan.objects.create(artist=artist)
        subscription = ArtistSubscription.objects.create(
            user=self.listener, artist=artist, plan=plan, status="ACTIVE",
            started_at=now - timedelta(days=2), expires_at=now - timedelta(days=1),
        )
        self.assertIsNone(self.client.get(url).data["track_url"])

        subscription.expires_at = now + timedelta(days=1)
        subscription.save(update_fields=["expires_at"])
        with patch("music.services.playback.storages", new_callable=MagicMock) as storages:
            storages.__getitem__.return_value.url.return_value = "https://storage.example.com/signed"
            subscriber = self.client.get(url)
        self.assertEqual(subscriber.status_code, 200)
        self.assertTrue(subscriber.data["is_subscription_only"])
        self.assertEqual(subscriber.data["track"], "https://storage.example.com/signed")
        self.assertEqual(subscriber.data["track_url"], subscriber.data["track"])
