# accounts/admin_serializers.py

from rest_framework import serializers
from accounts.models import UserListener 




class AdminUserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    has_active_subscription = serializers.BooleanField(read_only=True)

    favorite_genres_count = serializers.SerializerMethodField()
    favorite_artists_count = serializers.SerializerMethodField()

    class Meta:
        model = UserListener

        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "profile_pic",
            "is_artist",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
            "has_active_subscription",
            "favorite_genres_count",
            "favorite_artists_count",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "has_active_subscription",
            "favorite_genres_count",
            "favorite_artists_count",
        ]

    def get_profile_pic(self, obj):
        return obj.get_image()

    def get_favorite_genres_count(self, obj):
        return obj.favorite_genres.count()

    def get_favorite_artists_count(self, obj):
        return obj.favorite_artists.count()


class AdminUserCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = UserListener

        fields = [
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "is_artist",
            "is_active",
            "is_staff",
            "is_superuser",
        ]

    def validate_email(self, value):
        if UserListener.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate_username(self, value):
        if UserListener.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )

        return value

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = UserListener(
            **validated_data
        )

        user.set_password(password)
        user.save()

        return user
    
    
    
