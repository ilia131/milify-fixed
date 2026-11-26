from rest_framework import serializers

from music.models import (
    Songs,
    TrackArtist,
)


class AdminTrackArtistSerializer(serializers.ModelSerializer):
    artist_id = serializers.IntegerField(
        source="artist.id",
        read_only=True
    )

    artistname = serializers.CharField(
        source="artist.artistname",
        read_only=True
    )

    class Meta:
        model = TrackArtist
        fields = [
            "artist_id",
            "artistname",
            "role",
            "order",
        ]


class AdminSongSerializer(serializers.ModelSerializer):

    artists = serializers.SerializerMethodField()

    genre_name = serializers.CharField(
        source="genre.name",
        read_only=True,
        allow_null=True
    )

    album_title = serializers.CharField(
        source="album.title",
        read_only=True,
        allow_null=True
    )

    image = serializers.SerializerMethodField()
    track = serializers.SerializerMethodField()

    class Meta:
        model = Songs

        fields = [
            "id",
            "unique_id",

            "title",
            "description",

            "artists",

            "genre",
            "genre_name",

            "album",
            "album_title",
            "track_number",

            "image",
            "track",

            "popularity",
            "tempo",
            "energy",
            "danceability",
            "loudness",
            "valence",
            "acousticness",

            "verified",

            "total_revenue",
            "plays_last_24h",
            "unique_listeners",
            "play_count",
            "total_listen_time",

            "release_date",
            "is_published",

"release_date",
        ]

        read_only_fields = [
            "id",
            "unique_id",
            "artists",
            "genre_name",
            "album_title",
            "total_revenue",
            "plays_last_24h",
            "unique_listeners",
            "play_count",
            "total_listen_time",
"release_date",
        ]

    def get_artists(self, obj):
        relations = (
            obj.trackartist_set
            .select_related("artist")
            .all()
        )

        return AdminTrackArtistSerializer(
            relations,
            many=True
        ).data

    def get_image(self, obj):
        request = self.context.get("request")

        if not obj.image:
            return ""

        if request:
            return request.build_absolute_uri(
                obj.image.url
            )

        return obj.image.url

    def get_track(self, obj):
        request = self.context.get("request")

        if not obj.track:
            return ""

        if request:
            return request.build_absolute_uri(
                obj.track.url
            )

        return obj.track.url
    

class AdminSongCreateSerializer(serializers.ModelSerializer):

    artist_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    class Meta:
        model = Songs

        fields = [
            "title",
            "description",

            "artist_ids",

            "genre",
            "album",
            "track_number",

            "image",
            "track",

            "popularity",
            "tempo",
            "energy",
            "danceability",
            "loudness",
            "valence",
            "acousticness",

            "verified",
            "is_published",

            "release_date",
        ]

    def validate_artist_ids(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one artist is required."
            )

        from artists.models import Artist

        artists = Artist.objects.filter(
            id__in=value
        )

        if artists.count() != len(set(value)):
            raise serializers.ValidationError(
                "One or more artists were not found."
            )

        return value

    def validate(self, attrs):

        album = attrs.get("album")

        if album:
            artist_ids = attrs.get(
                "artist_ids",
                []
            )

            if album.artist_id not in artist_ids:
                raise serializers.ValidationError({
                    "album":
                    "The album artist must be one of the track artists."
                })

        return attrs

    def create(self, validated_data):

        artist_ids = validated_data.pop(
            "artist_ids"
        )

        song = Songs.objects.create(
            **validated_data
        )

        TrackArtist.objects.bulk_create([
            TrackArtist(
                track=song,
                artist_id=artist_id,
                role="main" if index == 0 else "feature",
                order=index
            )
            for index, artist_id in enumerate(
                artist_ids
            )
        ])

        return song
    
    

class AdminSongUpdateSerializer(serializers.ModelSerializer):

    artist_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Songs

        fields = [
            "title",
            "description",

            "artist_ids",

            "genre",
            "album",
            "track_number",

            "image",
            "track",

            "popularity",
            "tempo",
            "energy",
            "danceability",
            "loudness",
            "valence",
            "acousticness",

            "verified",
            "is_published",

            "release_date",
        ]

    def validate_artist_ids(self, value):
        from artists.models import Artist

        if not value:
            raise serializers.ValidationError(
                "At least one artist is required."
            )

        artists_count = Artist.objects.filter(
            id__in=value
        ).count()

        if artists_count != len(set(value)):
            raise serializers.ValidationError(
                "One or more artists were not found."
            )

        return value

    def update(self, instance, validated_data):

        artist_ids = validated_data.pop(
            "artist_ids",
            None
        )

        instance = super().update(
            instance,
            validated_data
        )

        if artist_ids is not None:

            TrackArtist.objects.filter(
                track=instance
            ).delete()

            TrackArtist.objects.bulk_create([
                TrackArtist(
                    track=instance,
                    artist_id=artist_id,
                    role=(
                        "main"
                        if index == 0
                        else "feature"
                    ),
                    order=index
                )
                for index, artist_id in enumerate(
                    artist_ids
                )
            ])

        return instance
    
    
    

from rest_framework import serializers
from .models import Playlist, PlaylistTrack


class AdminPlaylistTrackSerializer(serializers.ModelSerializer):
    song_id = serializers.IntegerField(source="song.id", read_only=True)
    song_unique_id = serializers.UUIDField(
        source="song.unique_id",
        read_only=True
    )
    song_title = serializers.CharField(
        source="song.title",
        read_only=True
    )
    song_image = serializers.SerializerMethodField()
    artists = serializers.SerializerMethodField()

    class Meta:
        model = PlaylistTrack
        fields = [
            "id",
            "song_id",
            "song_unique_id",
            "song_title",
            "song_image",
            "artists",
            "position",
        ]

    def get_song_image(self, obj):
        if not obj.song.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                obj.song.image.url
            )

        return obj.song.image.url

    def get_artists(self, obj):
        return [
            {
                "id": artist.id,
                "artistname": artist.artistname,
            }
            for artist in obj.song.artist.all()
        ]


class AdminPlaylistSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    user_email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    tracks_count = serializers.IntegerField(
        read_only=True
    )

    tracks = AdminPlaylistTrackSerializer(
        source="playlisttrack_set",
        many=True,
        read_only=True
    )

    class Meta:
        model = Playlist
        fields = [
            "id",
            "unique_id",
            "name",
            "username",
            "user_email",
            "tracks_count",
            "tracks",
        ]