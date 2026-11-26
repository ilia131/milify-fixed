from fastapi import FastAPI

from .schemas import (
    RecommendationRequest,
    RecommendationResponse,
)

from .recommender import RecommendationEngine


app = FastAPI(
    title="Milify ML Service",
    version="1.0.0",
)


engine = RecommendationEngine()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "milify-ml",
        "model_loaded": engine.model is not None,
    }


@app.post(
    "/recommend",
    response_model=RecommendationResponse,
)
def recommend(request: RecommendationRequest):
    recommendations = engine.recommend(
        request.user,
        request.songs,
    )

    return {
        "recommendations": recommendations
    }