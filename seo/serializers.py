from django.conf import settings

from rest_framework import serializers

from .models import ArtistSEO


class ArtistSEOSerializer(serializers.ModelSerializer):

    type = serializers.SerializerMethodField()
    uuid = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    canonical_url = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()
    robots = serializers.SerializerMethodField()

    open_graph = serializers.SerializerMethodField()
    twitter = serializers.SerializerMethodField()
    json_ld = serializers.SerializerMethodField()

    class Meta:
        model = ArtistSEO

        fields = [
            "type",
            "uuid",
            "name",
            "bio",
            "image",
            "title",
            "description",
            "canonical_url",
            "keywords",
            "robots",
            "open_graph",
            "twitter",
            "json_ld",
        ]

    # =========================================================
    # BASIC
    # =========================================================

    def get_type(self, obj):
        return "artist"

    def get_uuid(self, obj):
        return str(obj.artist.uuid)

    def get_name(self, obj):
        return obj.artist.artistname or ""

    def get_bio(self, obj):
        return obj.artist.bio or ""

    # =========================================================
    # IMAGE
    # =========================================================

    def get_image(self, obj):

        # Custom SEO image
        if obj.og_image:
            return obj.og_image

        request = self.context.get("request")

        artist = obj.artist

        if not artist.profile_pic:
            return ""

        # Django absolute URL
        if request:
            return request.build_absolute_uri(
                artist.profile_pic.url
            )

        return artist.profile_pic.url

    # =========================================================
    # TITLE
    # =========================================================

    def get_title(self, obj):

        artist_name = (
            obj.artist.artistname
            or "Artist"
        )

        if obj.title:
            return obj.title.strip()

        return (
            f"{artist_name} | "
            f"آهنگ ها و موزیک های {artist_name} | Milify"
        )

    # =========================================================
    # DESCRIPTION
    # =========================================================

    def get_description(self, obj):

        if obj.description:
            return obj.description.strip()[:160]

        bio = (
            obj.artist.bio
            or ""
        ).strip()

        if bio:
            return bio[:160]

        artist_name = (
            obj.artist.artistname
            or "این هنرمند"
        )

        return (
            f"گوش دادن به آهنگ ها، موزیک ها و آثار "
            f"{artist_name} در میلیفای."
        )[:160]

    # =========================================================
    # CANONICAL URL
    # =========================================================

    def get_canonical_url(self, obj):

        if obj.canonical_url:
            return obj.canonical_url

        frontend_url = getattr(
            settings,
            "MILIFY_FRONTEND_URL",
            "",
        )


        frontend_url = frontend_url.rstrip("/")

        if not frontend_url:
            return ""

        return f"{frontend_url}/artist/{obj.artist.uuid}/"

    # =========================================================
    # KEYWORDS
    # =========================================================

    def get_keywords(self, obj):

        if obj.keywords:

            return [
                keyword.strip()
                for keyword in obj.keywords.split(",")
                if keyword.strip()
            ]

        artist_name = (
            obj.artist.artistname
            or ""
        )

        if not artist_name:
            return []

        return [
            artist_name,
            f"آهنگ {artist_name}",
            f"موزیک {artist_name}",
            f"آهنگ های {artist_name}",
            f"موزیک های {artist_name}",
            f"{artist_name} songs",
            f"{artist_name} music",
        ]

    # =========================================================
    # ROBOTS
    # =========================================================

    def get_robots(self, obj):

        if not obj.is_active:
            return "noindex, nofollow"

        if not obj.is_indexable:
            return "noindex, nofollow"

        return obj.robots or "index, follow"

    # =========================================================
    # OPEN GRAPH
    # =========================================================

    def get_open_graph(self, obj):

        title = (
            obj.og_title
            or self.get_title(obj)
        )

        description = (
            obj.og_description
            or self.get_description(obj)
        )

        image = (
            obj.og_image
            or self.get_image(obj)
        )

        return {
            "title": title,
            "description": description,
            "image": image,
            "type": "profile",
            "url": self.get_canonical_url(obj),
        }

    # =========================================================
    # TWITTER
    # =========================================================

    def get_twitter(self, obj):

        title = (
            obj.twitter_title
            or obj.og_title
            or self.get_title(obj)
        )

        description = (
            obj.twitter_description
            or obj.og_description
            or self.get_description(obj)
        )

        image = (
            obj.twitter_image
            or obj.og_image
            or self.get_image(obj)
        )

        return {
            "card": "summary_large_image",
            "title": title,
            "description": description,
            "image": image,
        }

    # =========================================================
    # JSON-LD
    # =========================================================

    def get_json_ld(self, obj):

        artist_name = (
            obj.artist.artistname
            or "Artist"
        )

        description = self.get_description(obj)
        image = self.get_image(obj)
        canonical_url = self.get_canonical_url(obj)

        data = {
            "@context": "https://schema.org",
            "@type": "MusicGroup",
            "name": artist_name,
            "description": description,
            "url": canonical_url,
        }

        if image:
            data["image"] = image

        return data
    
    
    

from django.conf import settings

from rest_framework import serializers

from .models import SongSEO


class SongSEOSerializer(serializers.ModelSerializer):

    type = serializers.SerializerMethodField()

    unique_id = serializers.SerializerMethodField()

    name = serializers.SerializerMethodField()

    description = serializers.SerializerMethodField()

    image = serializers.SerializerMethodField()

    artist_name = serializers.SerializerMethodField()

    title = serializers.SerializerMethodField()

    seo_description = serializers.SerializerMethodField()

    canonical_url = serializers.SerializerMethodField()

    keywords = serializers.SerializerMethodField()

    robots = serializers.SerializerMethodField()

    open_graph = serializers.SerializerMethodField()

    twitter = serializers.SerializerMethodField()

    json_ld = serializers.SerializerMethodField()

    class Meta:
        model = SongSEO

        fields = [
            "type",
            "unique_id",
            "name",
            "description",
            "image",
            "artist_name",
            "title",
            "seo_description",
            "canonical_url",
            "keywords",
            "robots",
            "open_graph",
            "twitter",
            "json_ld",
        ]

    def get_type(self, obj):
        return "song"

    def get_unique_id(self, obj):
        return str(obj.song.unique_id)

    def get_name(self, obj):
        return obj.song.title or ""

    def get_description(self, obj):
        return obj.song.description or ""

    def get_image(self, obj):

        if obj.og_image:
            return obj.og_image

        request = self.context.get("request")

        song = obj.song

        if not song.image:
            return ""

        if request:
            return request.build_absolute_uri(
                song.image.url
            )

        return song.image.url

    def get_artist_name(self, obj):

        artists = obj.song.get_artists()

        if not artists:
            return ""

        return ", ".join(
            artist.artistname
            for artist in artists
            if artist.artistname
        )

    def get_title(self, obj):

        song = obj.song

        song_name = song.title or "آهنگ"

        artist_name = (
            self.get_artist_name(obj)
            or "هنرمند"
        )

        if obj.title:
            return obj.title.strip()

        return (
            f"{song_name} - "
            f"{artist_name} | "
            f"دانلود و گوش دادن | Milify"
        )

    def get_seo_description(self, obj):

        song = obj.song

        if obj.description:
            return obj.description.strip()[:160]

        if song.description:
            return song.description.strip()[:160]

        song_name = song.title or "این آهنگ"

        artist_name = (
            self.get_artist_name(obj)
            or "هنرمند"
        )

        return (
            f"گوش دادن به آهنگ {song_name} "
            f"از {artist_name} در میلیفای."
        )[:160]

    def get_canonical_url(self, obj):

        if obj.canonical_url:
            return obj.canonical_url

        frontend_url = getattr(
            settings,
            "MILIFY_FRONTEND_URL",
            "",
        )

        frontend_url = frontend_url.rstrip("/")

        if not frontend_url:
            return ""

        return (
            f"{frontend_url}"
            f"/track/{obj.song.unique_id}/"
        )

    def get_keywords(self, obj):

        if obj.keywords:

            return [
                keyword.strip()
                for keyword in obj.keywords.split(",")
                if keyword.strip()
            ]

        song = obj.song

        song_name = song.title or ""

        artist_name = (
            self.get_artist_name(obj)
        )

        keywords = []

        if song_name:
            keywords.extend([
                song_name,
                f"آهنگ {song_name}",
                f"موزیک {song_name}",
                f"{song_name} song",
                f"{song_name} music",
            ])

        if artist_name:
            keywords.extend([
                artist_name,
                f"آهنگ {artist_name}",
                f"موزیک {artist_name}",
            ])

        if song_name and artist_name:
            keywords.extend([
                f"{song_name} {artist_name}",
                f"{artist_name} {song_name}",
            ])

        return keywords

    def get_robots(self, obj):

        if not obj.is_active:
            return "noindex, nofollow"

        if not obj.is_indexable:
            return "noindex, nofollow"

        return obj.robots or "index, follow"

    def get_open_graph(self, obj):

        title = (
            obj.og_title
            or self.get_title(obj)
        )

        description = (
            obj.og_description
            or self.get_seo_description(obj)
        )

        image = (
            obj.og_image
            or self.get_image(obj)
        )

        return {
            "title": title,
            "description": description,
            "image": image,
            "type": "music.song",
            "url": self.get_canonical_url(obj),
        }

    def get_twitter(self, obj):

        title = (
            obj.twitter_title
            or obj.og_title
            or self.get_title(obj)
        )

        description = (
            obj.twitter_description
            or obj.og_description
            or self.get_seo_description(obj)
        )

        image = (
            obj.twitter_image
            or obj.og_image
            or self.get_image(obj)
        )

        return {
            "card": "summary_large_image",
            "title": title,
            "description": description,
            "image": image,
        }

    def get_json_ld(self, obj):

        song = obj.song

        song_name = song.title or "آهنگ"

        artist_name = (
            self.get_artist_name(obj)
            or "هنرمند"
        )

        description = (
            self.get_seo_description(obj)
        )

        image = self.get_image(obj)

        canonical_url = (
            self.get_canonical_url(obj)
        )

        data = {
            "@context": "https://schema.org",
            "@type": "MusicRecording",
            "name": song_name,
            "description": description,
            "url": canonical_url,

            "byArtist": {
                "@type": "MusicGroup",
                "name": artist_name,
            },
        }

        if image:
            data["image"] = image

        if song.release_date:
            data["datePublished"] = (
                song.release_date.isoformat()
            )

        return data