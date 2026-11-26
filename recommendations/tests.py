from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase

from music.models import Songs
from .views import load_track2vec


class Track2VecTests(APITestCase):
    def test_checked_in_model_loads(self):
        model = load_track2vec(settings.TRACK2VEC_MODEL_PATH)
        self.assertIsNotNone(model)
        self.assertGreater(len(model.wv), 0)

    def test_missing_model_returns_only_published_fallback_tracks(self):
        song = Songs.objects.create(title="Source")
        public = Songs.objects.create(title="Published", play_count=6)
        Songs.objects.create(title="Unpublished", is_published=False, play_count=12)

        with TemporaryDirectory() as folder:
            with self.settings(TRACK2VEC_MODEL_PATH=Path(folder) / "missing.model"):
                response = self.client.get(reverse("track2vec", args=[song.unique_id]))

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual([item["id"] for item in response.data], [public.pk])
