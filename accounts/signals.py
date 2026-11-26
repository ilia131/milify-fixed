from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Wallet
from accounts.models import UserListener


@receiver(post_save, sender=UserListener)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.get_or_create(
            user=instance
        )
        
