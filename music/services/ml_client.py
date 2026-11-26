import os
from typing import Any

import requests


ML_SERVICE_URL = os.getenv(
    "ML_SERVICE_URL",
    "http://127.0.0.1:8001",
)


class MLRecommendationClient:
    def __init__(self):
        self.base_url = ML_SERVICE_URL.rstrip("/")

    def recommend(
        self,
        user_id: int,
        songs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        url = f"{self.base_url}/recommend"

        payload = {
            "user": {
                "user_id": user_id,
            },
            "songs": songs,
        }

        session = requests.Session()

        # جلوگیری از استفاده requests از HTTP_PROXY سیستم
        session.trust_env = False

        response = session.post(
            url,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("recommendations", [])


ml_client = MLRecommendationClient()