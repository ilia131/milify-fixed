from django.core.management.base import BaseCommand

from music.services.analytics import (
    update_plays_last_24h,
    update_unique_listeners
)

class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        update_plays_last_24h()
        update_unique_listeners()

        self.stdout.write("Song analytics updated")
