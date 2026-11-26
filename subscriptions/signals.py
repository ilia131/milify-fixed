from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Wallet
from accounts.models import User


def get_wallet_cache_key(user_id):
    return f"wallet:{user_id}"


@receiver(
    post_save,
    sender=User,
)
def create_user_wallet(
    sender,
    instance,
    created,
    **kwargs,
):

    if not created:
        return

    Wallet.objects.create(
        user=instance
    )


@receiver(
    post_save,
    sender=Wallet,
)
def update_wallet_cache(
    sender,
    instance,
    **kwargs,
):

    cache.set(
        get_wallet_cache_key(
            instance.user_id
        ),
        {
            "id": str(instance.id),
            "user_id": str(
                instance.user_id
            ),
            "balance": str(
                instance.balance
            ),
        },
        timeout=None,
    )