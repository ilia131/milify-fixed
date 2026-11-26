from django.db import transaction
from django.utils import timezone

from music.models import SongListen, UserSongInteraction


@transaction.atomic
def finalize_song_interaction(
    listen: SongListen,
    *,
    skipped: bool = False,
    completed: bool = False,
    source: str = "",
):
    if not listen.user:
        return None

    # جلوگیری از ثبت دوباره همین session
    if listen.play_counted:
        return None

    interaction, created = (
        UserSongInteraction.objects
        .select_for_update()
        .get_or_create(
            user=listen.user,
            song=listen.song,
        )
    )

    duration = listen.seconds_listened or 0

    interaction.play_count += 1
    interaction.total_listen_time += duration

    if skipped:
        interaction.skip_count += 1

    if completed:
        interaction.completed_count += 1

    interaction.avg_listen_time = (
        interaction.total_listen_time
        / interaction.play_count
    )

    interaction.skip_rate = (
        interaction.skip_count
        / interaction.play_count
    )

    interaction.completion_rate = (
        interaction.completed_count
        / interaction.play_count
    )

    interaction.last_session_id = listen.session_id
    interaction.last_source = source
    interaction.last_interaction_at = timezone.now()

    interaction.engagement_score = (
        interaction.avg_listen_time * 0.4
        + interaction.completion_rate * 30
        + interaction.play_count * 2
        + interaction.replay_count * 3
        + (5 if interaction.liked else 0)
        + (5 if interaction.favorited else 0)
        - interaction.skip_rate * 10
    )

    interaction.save()

    # خیلی مهم:
    listen.play_counted = True
    listen.save(update_fields=["play_counted"])

    return interaction