from music.services.playback import playable_track_url
from rest_framework import serializers

from music.models import Songs


class RecommendationSongSerializer(
    serializers.ModelSerializer
):
    score = serializers.FloatField(
        read_only=True
    )

    image = serializers.SerializerMethodField()
    track = serializers.SerializerMethodField()

    artistname = serializers.SerializerMethodField()
    artists = serializers.SerializerMethodField()

    genre_name = serializers.SerializerMethodField()
    album_name = serializers.SerializerMethodField()

    class Meta:
        model = Songs

        fields = [
            "id",
            "unique_id",

            "title",
            "description",
            "duration",

            "artistname",
            "artists",

            "image",
            "track",

            "genre",
            "genre_name",

            "category",

            "album",
            "album_name",

            "popularity",
            "tempo",
            "energy",
            "danceability",
            "loudness",

            "play_count",
            "unique_listeners",
            "plays_last_24h",
            "total_listen_time",

            "valence",
            "acousticness",

            "verified",
            "is_published",

            "release_date",

            "score",
        ]

    def get_image(self, obj):
        if not obj.image:
            return None

        try:
            return obj.image.url
        except ValueError:
            return None

    def get_track(self, obj):
        return playable_track_url(obj, self.context.get("request"))

    def get_artistname(self, obj):
        artist = (
            obj.artist
            .all()
            .first()
        )

        if not artist:
            return None

        return artist.artistname

    def get_artists(self, obj):
        return [
            artist.artistname
            for artist in obj.artist.all()
        ]

    def get_genre_name(self, obj):
        if not obj.genre:
            return None

        return obj.genre.name

    def get_album_name(self, obj):
        if not obj.album:
            return None

        return obj.album.title

