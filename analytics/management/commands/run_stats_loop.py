from django.core.management.base import BaseCommand
from time import sleep
from music.services.analytics import (
    update_plays_last_24h,
    update_unique_listeners
)

class Command(BaseCommand):
    help = "Update song stats every 10 minutes without cron"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Stats loop started..."))

        while True:
            try:
                update_plays_last_24h()
                update_unique_listeners()
                self.stdout.write(self.style.SUCCESS("Stats updated"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))

            sleep(600)  # 10 minutes
