from rest_framework import serializers
from .models import RecentlyPlayed
from music.serializers import SongPlayerSerializer


class RecentlyPlayedSerializer(serializers.ModelSerializer):
    song = SongPlayerSerializer(read_only=True)

    class Meta:
        model = RecentlyPlayed
        fields = [
            "id",
            "song",
            "played_at",
        ]
