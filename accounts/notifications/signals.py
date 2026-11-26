from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from artists.models import Artist
from music.models import Album, Songs

from .services import NotificationService


@receiver(post_save, sender=Artist)
def artist_created(
    sender,
    instance,
    created,
    **kwargs
):
    if not created:
        return

    if not instance.artistname:
        return

    transaction.on_commit(
        lambda: NotificationService.send_to_all_users(
            title="🎤 هنرمند جدید",
            message=f"{instance.artistname} به Milify پیوست.",
            notification_type="new_artist",
            url=f"/artist/{instance.artistname}",
        )
    )


@receiver(post_save, sender=Album)
def album_created(
    sender,
    instance,
    created,
    **kwargs
):
    if not created:
        return

    if not instance.is_published:
        return

    artist = instance.artist

    if not artist or not artist.artistname:
        return

    transaction.on_commit(
        lambda: NotificationService.send_to_all_users(
            title="💿 آلبوم جدید منتشر شد",
            message=f"آلبوم «{instance.title}» منتشر شد.",
            notification_type="new_album",
            url=f"/album/{artist.artistname}/{instance.title}",
        )
    )


@receiver(post_save, sender=Songs)
def song_created(
    sender,
    instance,
    created,
    **kwargs
):
    if not created:
        return

    if not instance.is_published:
        return

    transaction.on_commit(
        lambda: NotificationService.send_to_all_users(
            title="🎵 آهنگ جدید منتشر شد",
            message=f"آهنگ «{instance.title}» منتشر شد.",
            notification_type="new_song",
            url=f"/track/{instance.unique_id}",
        )
    )