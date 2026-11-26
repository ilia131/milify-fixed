from pydantic import BaseModel, Field


class UserSongInteractionFeatures(BaseModel):
    play_count: int = 0
    total_listen_time: int = 0
    avg_listen_time: float = 0.0
    skip_count: int = 0
    skip_rate: float = 0.0
    completed_count: int = 0
    completion_rate: float = 0.0
    engagement_score: float = 0.0


class UserTasteProfile(BaseModel):
    avg_tempo: float = 120.0
    avg_energy: float = 0.5
    avg_danceability: float = 0.5
    avg_valence: float = 0.5
    avg_acousticness: float = 0.5
    avg_popularity: float = 0.0
    total_play_count: int = 0
    total_listen_time: int = 0
    avg_completion_rate: float = 0.0
    avg_skip_rate: float = 0.0


class SongFeatures(BaseModel):
    song_id: int

    popularity: float = 0.0
    tempo: float = 120.0
    energy: float = 0.5
    danceability: float = 0.5
    valence: float = 0.0
    acousticness: float = 0.0

    unique_listeners: int = 0
    play_count: int = 0
    total_listen_time: int = 0
    plays_last_24h: int = 0
    song_age_days: float = 0.0

    interaction: UserSongInteractionFeatures = Field(
        default_factory=UserSongInteractionFeatures
    )

    user_profile: UserTasteProfile = Field(
        default_factory=UserTasteProfile
    )


class UserFeatures(BaseModel):
    user_id: int


class RecommendationRequest(BaseModel):
    user: UserFeatures
    songs: list[SongFeatures]


class RecommendationResult(BaseModel):
    song_id: int
    score: float


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationResult]