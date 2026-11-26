from django.db import transaction
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from accounts.models import UserListener
from artists.models import Artist


class CustomUserCreateSerializer(UserCreateSerializer):

    re_password = serializers.CharField(write_only=True)

    favorite_artists = serializers.SlugRelatedField(
        many=True,
        slug_field="artistname",
        queryset=Artist.objects.all(),
        required=False
    )

    class Meta(UserCreateSerializer.Meta):
        model = UserListener
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "re_password",
            "favorite_artists",
        )

    def validate_email(self, value):
        email = value.lower()
        if UserListener.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("This email is already registered.")
        return email

    def validate(self, attrs):
        
        if attrs["password"] != attrs["re_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match"}
            )
        super().validate({
            name: value for name, value in attrs.items()
            if name not in {"re_password", "favorite_artists"}
        })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("re_password")
        favorite_artists = validated_data.pop("favorite_artists", [])
        user = super().create(validated_data)
        if favorite_artists:
            user.favorite_artists.set(favorite_artists)
        return user
