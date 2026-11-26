from django.contrib import admin
from .models import Artist, ArtistPick
from accounts.models import UserListener
from django.contrib import admin

from .models import Artist, ArtistPick, FollowArtist, ArtistYouTubeVideo


class ArtistYouTubeVideoInline(admin.TabularInline):
    model = ArtistYouTubeVideo
    extra = 1
    fields = (
        "title",
        "embed_url",
        "thumbnail",
        "order",
        "is_active",
    )


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = (
        "artistname",
        "monthly_listeners",
        "is_featured",
        "created_at",
    )

    search_fields = (
        "artistname",
        "user__username",
    )

    list_filter = (
        "is_featured",
        "created_at",
    )

    inlines = [
        ArtistYouTubeVideoInline,
    ]
class ArtistPickInline(admin.StackedInline):
    model = ArtistPick
    extra = 0
    max_num = 1   # چون هر Artist فقط یک Pick دارد
    can_delete = True

 