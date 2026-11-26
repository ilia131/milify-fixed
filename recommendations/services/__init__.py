from music.models import Songs
from .ranking import rank_songs_for_playlist

def suggest_songs_for_playlist(user, playlist_unique_ids, limit=20):
    songs = list(Songs.objects.filter(unique_id__in=playlist_unique_ids, is_published=True))
    ranked = rank_songs_for_playlist(user, songs, limit)
    return [r.song for r in ranked]
