from django.utils import timezone

from .models import ArtistSubscription


def song_subscription_access(song, user):
    artists = list(song.artist.all())
    approved_ids = set(
        song.artist_subscription_access.filter(
            status="APPROVED"
        ).values_list("artist_id", flat=True)
    )
    artist_ids = {artist.pk for artist in artists}
    if not artist_ids or not artist_ids.issubset(approved_ids):
        return {"can_play": True, "requires_subscription": False}

    result = {"can_play": False, "requires_subscription": True}
    if user is None or not user.is_authenticated:
        return {**result, "reason": "LOGIN_REQUIRED"}

    now = timezone.now()
    subscribed = ArtistSubscription.objects.filter(
        user=user,
        artist_id__in=artist_ids,
        status="ACTIVE",
        started_at__lte=now,
        expires_at__gt=now,
    ).exists()
    if subscribed:
        return {**result, "can_play": True}

    return {
        **result,
        "reason": "SUBSCRIPTION_REQUIRED",
        "artists": [artist.artistname for artist in artists],
    }
