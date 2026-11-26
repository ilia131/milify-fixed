from rest_framework import serializers

from artists.models import Artist, FollowArtist


class AdminArtistSerializer(serializers.ModelSerializer):

    profile_pic = serializers.SerializerMethodField()
    background = serializers.SerializerMethodField()

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    is_active = serializers.BooleanField(
        source="user.is_active",
        read_only=True
    )

    followers_count = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Artist

        fields = [
            "id",
            "uuid",
            "artistname",
            "bio",
            "username",
            "email",
            "profile_pic",
            "background",
            "is_featured",
            "is_active",
            "monthly_listeners",
            "followers_count",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "uuid",
            "username",
            "email",
            "is_active",
            "followers_count",
            "created_at",
        ]

    def get_profile_pic(self, obj):
        request = self.context.get("request")

        if request:
            return obj.get_image(request)

        return ""

    def get_background(self, obj):
        request = self.context.get("request")

        if request:
            return obj.get_background(request)

        return ""


class AdminArtistCreateSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(
        write_only=True
    )

    class Meta:
        model = Artist

        fields = [
            "user_id",
            "artistname",
            "bio",
            "profile_pic",
            "background",
            "is_featured",
            "monthly_listeners",
        ]

    def validate_user_id(self, value):

        from accounts.models import UserListener

        try:
            user = UserListener.objects.get(
                id=value
            )
        except UserListener.DoesNotExist:
            raise serializers.ValidationError(
                "User not found."
            )

        if hasattr(user, "artist"):
            raise serializers.ValidationError(
                "This user already has an artist profile."
            )

        return value

    def create(self, validated_data):

        user_id = validated_data.pop(
            "user_id"
        )

        artist = Artist.objects.create(
            user_id=user_id,
            **validated_data
        )

        user = artist.user

        if not user.is_artist:
            user.is_artist = True
            user.save(
                update_fields=["is_artist"]
            )

        return artist


class AdminArtistUpdateSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Artist

        fields = [
            "artistname",
            "bio",
            "profile_pic",
            "background",
            "is_featured",
            "monthly_listeners",
        ]
        
class AdminFollowArtistSerializer(
    serializers.ModelSerializer
):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    artistname = serializers.CharField(
        source="artist.artistname",
        read_only=True
    )

    class Meta:

        model = FollowArtist

        fields = [
            "id",
            "username",
            "email",
            "artistname",
            "created_at",
        ]