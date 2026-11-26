from rest_framework import generics, permissions
from .models import RecentlyPlayed
from .serializers import RecentlyPlayedSerializer
from django.utils import timezone

def add_recent_play(user, song):
    RecentlyPlayed.objects.update_or_create(
        user=user,
        song=song,
        defaults={
            "played_at": timezone.now()
        }
    )


class RecentlyPlayedList(generics.ListAPIView):
    serializer_class = RecentlyPlayedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = (
            RecentlyPlayed.objects
            .filter(user=self.request.user)
            .select_related("song")
            .prefetch_related("song__artist")
        )

        artist_id = self.request.query_params.get("artist")

        if artist_id:
            queryset = queryset.filter(song__artist__id=artist_id)

        return queryset.order_by("-played_at")[:20]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

