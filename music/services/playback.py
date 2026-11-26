from django.core.files.storage import storages

from subscriptions.access import song_subscription_access


def playable_track_url(song, request, access=None):
    if not song.track:
        return None
    if access is None:
        access = song_subscription_access(song, getattr(request, "user", None))
    if not access["can_play"]:
        return None

    if access["requires_subscription"]:
        url = storages["private_tracks"].url(song.track.name)
    else:
        url = song.track.url
    return request.build_absolute_uri(url) if request else url
