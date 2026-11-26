import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from .main import app
from .recommender import RecommendationEngine
from .schemas import SongFeatures, UserFeatures


class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_repository_model_loads_and_scores_minimal_input(self):
        health = self.client.get("/health")
        self.assertTrue(health.json()["model_loaded"])
        response = self.client.post(
            "/recommend", json={"user": {"user_id": 1}, "songs": [{"song_id": 2}]}
        )
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()["recommendations"][0]
        self.assertEqual(result["song_id"], 2)
        self.assertGreaterEqual(result["score"], 0)

    def test_invalid_input_returns_422(self):
        response = self.client.post("/recommend", json={"user": {"user_id": 1}, "songs": [{}]})
        self.assertEqual(response.status_code, 422)

    def test_missing_and_corrupt_files_keep_fallback_working(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ml.joblib"
            for corrupt in (False, True):
                with self.subTest(corrupt=corrupt):
                    if corrupt:
                        path.write_bytes(b"invalid model")
                    engine = RecommendationEngine(path)
                    self.assertIsNone(engine.model)
                    ranked = engine.recommend(UserFeatures(user_id=1), [SongFeatures(song_id=2)])
                    self.assertEqual(ranked[0]["song_id"], 2)
