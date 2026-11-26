from django.db.models import QuerySet 
 
from music.models import Songs, UserSongInteraction 
 
from .feature_builder import build_song_features 
from music.ml.feature_engineering import ( 
    get_user_taste_profile, 
) 
 
from .ml_client import ml_client 
 
 
class RecommendationService: 
 
    DEFAULT_LIMIT = 10 
    MAX_LIMIT = 50 
 
    @classmethod 
    def get_recommendations( 
        cls, 
        user, 
        limit: int = DEFAULT_LIMIT, 
    ): 
 
        limit = min( 
            max(int(limit), 1), 
            cls.MAX_LIMIT, 
        ) 
 
        interacted_song_ids = set( 
            UserSongInteraction.objects 
            .filter(user=user) 
            .values_list( 
                "song_id", 
                flat=True, 
            ) 
        ) 
 
        songs: QuerySet[Songs] = ( 
            Songs.objects 
            .filter( 
                is_published=True 
            ) 
            .exclude( 
                id__in=interacted_song_ids 
            ) 
            .order_by( 
                "-plays_last_24h", 
                "-popularity", 
            ) 
        ) 
 
        songs = list( 
            songs[:100] 
        ) 
 
        if not songs: 
            return [] 
 
        user_profile = ( 
            get_user_taste_profile( 
                user_id=user.id 
            ) 
        ) 
 
        ml_songs = [] 
 
        for song in songs: 
 
            ml_songs.append( 
                build_song_features( 
                    song=song, 
                    interaction=None, 
                    user_profile=user_profile, 
                ) 
            ) 
 
        predictions = ml_client.recommend( 
            user_id=user.id, 
            songs=ml_songs, 
        ) 
 
        if not predictions: 
            return [] 
 
        scores = { 
            item["song_id"]: float( 
                item["score"] 
            ) 
            for item in predictions 
        } 
 
        result = [] 
 
        for song in songs: 
 
            score = scores.get( 
                song.id 
            ) 
 
            if score is None: 
                continue 
 
            result.append( 
                { 
                    "song": song, 
                    "score": score, 
                } 
            ) 
 
        result.sort( 
            key=lambda item: item["score"], 
            reverse=True, 
        ) 
 
        return result[:limit] 