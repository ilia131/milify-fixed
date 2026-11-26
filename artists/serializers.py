from rest_framework import serializers
from .models import Artist , ArtistYouTubeVideo
from music.models import Songs , ShortVideo 
from music.serializers import SongPlayerSerializer , ShortVideo2Serializer

from rest_framework import serializers
from .models import FollowArtist

from django.db.models import Sum
class ArtistYouTubeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistYouTubeVideo
        fields = [
            "id",
            "title",
            "embed_url",
            "thumbnail",
            "description",
            "is_active",
            "order",
            "created_at",
        ]
class ArtistDashboardSerializer(serializers.ModelSerializer):

    followers = serializers.SerializerMethodField()
    total_streams = serializers.SerializerMethodField()
    watch_time_hours = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    top_songs = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = [
            "id",
            "artistname",
            "monthly_listeners",
            "followers",
            "total_streams",
            "watch_time_hours",
            "revenue",
            "top_songs"
        ]

    def get_followers(self, obj):
        return obj.followers.count()

    def get_total_streams(self, obj):
        songs = Songs.objects.filter(artist=obj)
        return songs.aggregate(total=Sum("play_count"))["total"] or 0

    def get_watch_time_hours(self, obj):
        songs = Songs.objects.filter(artist=obj)
        total_sec = songs.aggregate(total=Sum("total_listen_time"))["total"] or 0
        return round(total_sec / 3600, 2)

    def get_revenue(self, obj):
        streams = self.get_total_streams(obj)
        return round(streams * 0.0025, 2)

    def get_top_songs(self, obj):
        songs = Songs.objects.filter(artist=obj).order_by("-play_count")[:5]

        return [
            {
                "id": s.id,
                "title": s.title,
                "play_count": s.play_count,
                "image": s.get_image_url()
            }
            for s in songs
        ]

class FollowArtistSerializer(serializers.ModelSerializer):

    artist_name = serializers.CharField(source="artist.artistname", read_only=True)
    artist_uuid = serializers.UUIDField(source="artist.uuid", read_only=True)

    class Meta:
        model = FollowArtist
        fields = [
            "id",
            "artist_uuid",
            "artist_name",
            "created_at",
        ]


class ArtistListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ["id", "artistname", "profile_pic"]
    
    def get_profile_pic(self, obj):
        request = self.context.get("request")
        if obj.profile_pic:
            return request.build_absolute_uri(obj.profile_pic.url)
        return None

    def get_background(self, obj):
        request = self.context.get("request")
        if obj.background:
            return request.build_absolute_uri(obj.background.url)
        return None
    

class ArtistCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artist
        fields = [
            "user",
            "artistname",
            "bio",
            "monthly_listeners",
            "profile_pic",
            "background",
            "is_featured",
        ]

    def create(self, validated_data):
        if "user" not in validated_data:
            validated_data["user"] = self.context["request"].user if self.context.get("request") else None
        return super().create(validated_data)


class ArtistUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artist
        fields = [
            "bio",
            "monthly_listeners",
            "profile_pic",
            "background",
            "is_featured",
        ]
class ArtistSerializer(serializers.ModelSerializer):
    youtube_videos = ArtistYouTubeVideoSerializer(
        many=True,
        read_only=True,
    )

    songs = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    background = serializers.SerializerMethodField()
    artist_pick = serializers.SerializerMethodField()
    shorts = serializers.SerializerMethodField()
    
    class Meta:
        model = Artist
        fields = "__all__"
        
    def get_shorts(self , obj):
        request = self.context.get("request")
        shorts = ShortVideo.objects.filter(main_artist= obj)
      
        
        return ShortVideo2Serializer(shorts , many=True, context={"request" : request}).data
        
        

    def get_songs(self, obj):
        request = self.context.get("request")
        songs = (
            Songs.objects
            .filter(artist=obj)
            .order_by('-plays_last_24h', '-play_count', '-release_date')
        )
        return SongPlayerSerializer(songs, many=True, context={"request": request}).data
    
    def get_profile_pic(self, obj):
        request = self.context.get("request")
        return obj.get_image(request)

    def get_background(self, obj):
        request = self.context.get("request")
        return obj.get_background(request)

    def get_artist_pick(self, obj):
        pick = getattr(obj, "artist_pick", None)
        if not pick:
            return None

        request = self.context.get("request")

        item = pick.item
        item_type = pick.content_type.model

        base = {
            "type": item_type,
            "message": pick.message,
        }

        def absolute(url):
            if not url:
                return None
            return request.build_absolute_uri(url)

        # SONG
        if item_type == "songs":
            return {
                **base,
                "id": item.id,
                "title": item.title,
                "image": absolute(item.image.url) if item.image else None,
            }

        # ALBUM
        if item_type == "album":
            return {
                **base,
                "id": item.id,
                "title": item.title,
                "image": absolute(item.cover.url) if item.cover else None,
            }

        return base