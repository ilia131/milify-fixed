from music.services.playback import playable_track_url
from subscriptions.access import song_subscription_access
from rest_framework import serializers
from music.models import Songs , Album , Lyrics  , LikedSong , PlaylistTrack , Playlist , Genre
from artists.models import Artist
from rest_framework import serializers
from .models import ShortVideo
from django.utils import timezone

from .models import (
    ShortVideo,
    ShortVideoComment,
)

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Songs
        fields = "__all__"
        
        
class Song2Serializer(serializers.ModelSerializer):

    class Meta:
        model = Songs
        fields = [
            "id",
            "title",
            "description",
            "track",
            "image",
            "genre",
            "tempo",
            "energy",
            "danceability",
            "valence",
            "acousticness",
            "loudness",
        ]

class LyricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lyrics
        fields = ["time", "line"]


class ShortVideoSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    shares_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = ShortVideo

        fields = [
            "uuid",
            "user",
            "username",
            "main_artist",
            "featured_artists",
            "audio_track",
            "video",
            "thumbnail",
            "caption",
            "duration",
            "views",
            "is_official",
            "likes_count",
            "comments_count",
            "shares_count",
            "is_liked",
            "allow_comments",
            "score",
            "created_at",
        ]

        read_only_fields = [
            "uuid",
            "views",
            "likes_count",
            "comments_count",
            "shares_count",
            "is_liked",
            "created_at",
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments_count

    def get_is_liked(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return obj.likes.filter(
            id=request.user.id
        ).exists()
    
    # def get_artists(self, obj):
    #     from artists.serializers import ArtistSerializer
    #     return ArtistSerializer(
    #         obj.artists.get().artist_name,
    #         many=True,
    #         context=self.context
    #     ).data

    
    
    def get_video_url(self, obj):
        # راه حل ایمن:
        request = self.context.get("request")
        if obj.video:
            # اگر request موجود بود از آن استفاده کن، در غیر این صورت فقط URL را برگردان
            if request is not None:
                return request.build_absolute_uri(obj.video.url)
            return obj.video.url 
        return None
      
#Song Player
class SongPlayerSerializer(serializers.ModelSerializer):
    genre_name = serializers.CharField(source="genre.name", read_only=True)
    image_url = serializers.SerializerMethodField()
    track_url = serializers.SerializerMethodField()
    track = serializers.SerializerMethodField()
    artistname = serializers.SerializerMethodField()
    artists = serializers.SerializerMethodField()
    is_subscription_only = serializers.SerializerMethodField()

    lyrics = LyricsSerializer(source="lyrics_lines", many=True, read_only=True)
    album_name = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    shorts = ShortVideoSerializer(
        source="short_videos",
        many=True,
        read_only=True
    )

    class Meta:
        model = Songs
        fields = "__all__"

    def get_is_liked(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return obj.liked_by.filter(user=request.user).exists()

    def get_image_url(self, obj):
        request = self.context.get("request")

        if obj.image and hasattr(obj.image, "url"):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url

        return None

    def get_track_url(self, obj):
        request = self.context.get("request")

        return playable_track_url(obj, request, self._subscription_access(obj))

    def get_track(self, obj):
        return self.get_track_url(obj)

    def _subscription_access(self, obj):
        if not hasattr(self, "_access_by_song"):
            self._access_by_song = {}
        if obj.pk not in self._access_by_song:
            request = self.context.get("request")
            self._access_by_song[obj.pk] = song_subscription_access(
                obj, getattr(request, "user", None)
            )
        return self._access_by_song[obj.pk]

    def get_artists(self, obj):
        return [
            relation.artist.artistname
            for relation in obj.trackartist_set.all()
            if relation.artist
        ]

    def get_artistname(self, obj):
        relation = obj.trackartist_set.filter(role="main").first()

        if not relation:
            relation = obj.trackartist_set.first()

        if relation and relation.artist:
            return relation.artist.artistname

        return None

    def get_album_name(self, obj):
        if obj.album:
            return obj.album.title
        return None
    
    def get_is_subscription_only(self, obj):
        return self._subscription_access(obj)["requires_subscription"]


class AlbumSerializer(serializers.ModelSerializer):
    tracks = SongPlayerSerializer(many=True, read_only=True)
    artist = serializers.SerializerMethodField()
    class Meta:
        model = Album
        fields = (
            "id",
            "title",
            "release_date",
            "cover",
            "tracks",
            "artist",
        )

    def get_artist(self, obj):
        if obj.artist:
            return [
                   {"name": obj.artist.artistname}
                ]
            
        return None



class Album2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "description",
            "cover",
            "release_date",
            "is_published",
        ]


#SHORTCOMMENT
class ShortVideoCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    user_id = serializers.IntegerField(
        source="user.id",
        read_only=True
    )

    likes_count = serializers.SerializerMethodField()

    is_liked = serializers.SerializerMethodField()

    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = ShortVideoComment

        fields = [
            "id",
            "user_id",
            "username",
            "text",
            "created_at",
            "updated_at",
            "parent",
            "likes_count",
            "is_liked",
            "replies_count",
        ]

        read_only_fields = [
            "id",
            "user_id",
            "username",
            "created_at",
            "updated_at",
            "likes_count",
            "is_liked",
            "replies_count",
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return obj.likes.filter(
            id=request.user.id
        ).exists()

    def get_replies_count(self, obj):
        return obj.replies.count()

    
    

class ShortVideoDetailSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = ShortVideo
        fields = "__all__"

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    
    


class ShortVideo2Serializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    video_url = serializers.SerializerMethodField()
    audio_track_data = serializers.SerializerMethodField()

    class Meta:
        model = ShortVideo
        fields = "__all__"
        read_only_fields = ("user", "main_artist")
        
    
    def get_video_url(self, obj):
        request = self.context.get("request")

        if obj.video:
            return request.build_absolute_uri(obj.video.url)

        return None
    
    
    def get_audio_track_data(self, obj):
        if not obj.audio_track:
            return None

        return {
            "id": obj.audio_track.id,
            "title": obj.audio_track.title,
        }
        
    
    
    def validate(self, attrs):
            request = self.context["request"]
            user = request.user
            audio_track = attrs.get("audio_track")

            if audio_track:
                exists = ShortVideo.objects.filter(
                    user=user,
                    audio_track=audio_track
                ).exists()

                if exists:
                    raise serializers.ValidationError(
                        "برای این آهنگ قبلاً یک شورت‌ویدیو توسط شما آپلود شده است."
                    )

            return attrs
        
        
        



class BigCardArtistSerializer(serializers.ModelSerializer):
    top_tracks = serializers.SerializerMethodField()
    profile_pic_url = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ["id", "artistname", "profile_pic_url", "top_tracks"]

    def get_profile_pic_url(self, obj):
        request = self.context.get("request")
        if request and obj.profile_pic:
            return request.build_absolute_uri(obj.profile_pic.url)
        if obj.profile_pic:
            return obj.profile_pic.url
        return None

    def get_top_tracks(self, obj):
        now = timezone.now()
        tracks = obj.tracks.all()

        scored_tracks = []

        for track in tracks:
            score = 0

            score += track.plays_last_24h * 2.5
            score += track.unique_listeners * 0.4
            score += track.play_count * 0.2

            days = (now - track.release_date).days
            freshness = max(0, 100 - days)
            score += freshness

            scored_tracks.append((track, score))

        # مرتب‌سازی براساس امتیاز
        scored_tracks.sort(key=lambda x: x[1], reverse=True)

        # فقط ترک (بدون score) را بردار
        ordered_tracks = [t[0] for t in scored_tracks[:3]]

        return SongPlayerSerializer(ordered_tracks, many=True, context=self.context).data
    
    
    

class LikedSongSerializer(serializers.ModelSerializer):
    song = SongPlayerSerializer(read_only=True)

    class Meta:
        model = LikedSong
        fields = ["id", "song", "created_at"]
        
        
        

class PlaylistTrackSerializer(serializers.ModelSerializer):
    song = SongPlayerSerializer(read_only=True)
    
    class Meta:
        model = PlaylistTrack
        fields = ['id', 'song', 'added_at', 'position']

class PlaylistSerializer(serializers.ModelSerializer):
    tracks_count = serializers.IntegerField(source='playlisttrack_set.count', read_only=True)
    tracks = PlaylistTrackSerializer(source='playlisttrack_set', many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = ['unique_id', 'name', 'user', 'tracks_count', 'tracks']
        read_only_fields = ['user', 'unique_id']
        
        


class GenreBrowseSerializer(serializers.ModelSerializer):
    songs_count = serializers.IntegerField(read_only=True)
    # top_songs = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = [
            "id",
            "name",
            "songs_count",
            "cover_image",
            # "top_songs",
        ]

    # def get_top_songs(self, obj):
    #     request = self.context.get("request")

    #     songs = (
    #         Songs.objects.filter(genre=obj, is_published=True)
    #         .select_related("genre", "album")
    #         .prefetch_related("artist")
    #         .order_by("-plays_last_24h", "-play_count")[:5]
    #     )

    #     return SongPlayerSerializer(songs, many=True, context={"request": request}).data

    def get_cover_image(self, obj):
        # اگر خود Genre فیلد cover داشته باشد
        if hasattr(obj, "cover") and obj.cover:
            return obj.cover.url

        # اگر ندارد، از اولین آهنگ منتشرشده استفاده کن
        first_song = (
            Songs.objects.filter(genre=obj, is_published=True)
            .exclude(image=None)
            .first()
        )
        if first_song:
            return first_song.get_image_url()

        return None
    
    

class GenreDetailSerializer(serializers.ModelSerializer):

    songs_count = serializers.IntegerField(read_only=True)
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = [
            "id",
            "name",
            "songs_count",
            "cover_image",
        ]

    def get_cover_image(self, obj):
        request = self.context.get("request")

        first_song = (
            Songs.objects
            .filter(
                genre=obj,
                is_published=True
            )
            .exclude(image="")
            .first()
        )

        if first_song and first_song.image:
            return request.build_absolute_uri(first_song.image.url)

        return None
    
    



