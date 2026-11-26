import random

from music.models import Songs, UserSongInteraction

from music.ml.feature_engineering import (
    get_feature_names,
    get_user_taste_profile,
    build_training_features,
)


NEGATIVE_SAMPLES_PER_POSITIVE = 3
RANDOM_SEED = 42
POSITIVE_TARGET_THRESHOLD = 3.0


def calculate_target(interaction):
    score = 0.0

    if interaction.play_count > 0:
        score += 1.0

    if interaction.total_listen_time >= 30:
        score += 1.0

    if interaction.total_listen_time >= 60:
        score += 1.0

    if interaction.completion_rate >= 0.5:
        score += 2.0

    if interaction.completion_rate >= 0.8:
        score += 2.0

    if interaction.replay_count > 0:
        score += 2.0

    if interaction.liked:
        score += 3.0

    if interaction.favorited:
        score += 3.0

    if interaction.skip_rate >= 0.5:
        score -= 2.0

    if interaction.skip_rate >= 0.8:
        score -= 2.0

    return float(score)


def get_target(interaction):
    return int(
        calculate_target(interaction)
        >= POSITIVE_TARGET_THRESHOLD
    )


def get_positive_interactions():
    interactions = (
        UserSongInteraction.objects
        .select_related("song")
        .order_by("user_id", "song_id")
    )

    return [
        interaction
        for interaction in interactions
        if get_target(interaction) == 1
    ]


def get_negative_interactions():
    interactions = (
        UserSongInteraction.objects
        .select_related("song")
        .order_by("user_id", "song_id")
    )

    return [
        interaction
        for interaction in interactions
        if interaction.play_count > 0
        and get_target(interaction) == 0
    ]


def get_user_interacted_song_ids(user_id):
    return set(
        UserSongInteraction.objects
        .filter(user_id=user_id)
        .values_list(
            "song_id",
            flat=True,
        )
    )


def get_negative_songs(
    user_id,
    all_song_ids,
    count=NEGATIVE_SAMPLES_PER_POSITIVE,
    rng=None,
):

    if rng is None:
        rng = random.Random(
            RANDOM_SEED
        )

    interacted_song_ids = (
        get_user_interacted_song_ids(
            user_id
        )
    )

    available_song_ids = [
        song_id
        for song_id in all_song_ids
        if song_id not in interacted_song_ids
    ]

    if not available_song_ids:
        return []

    sample_size = min(
        count,
        len(available_song_ids),
    )

    return rng.sample(
        available_song_ids,
        sample_size,
    )


def build_positive_row(interaction):

    user_profile = (
        get_user_taste_profile(
            user_id=interaction.user_id,
            exclude_song_id=interaction.song_id,
        )
    )

    features = build_training_features(
        song=interaction.song,
        interaction=interaction,
        user_profile=user_profile,
    )

    features["user_id"] = interaction.user_id
    features["song_id"] = interaction.song.id
    features["target"] = 1

    return features


def build_real_negative_row(interaction):

    user_profile = (
        get_user_taste_profile(
            user_id=interaction.user_id,
            exclude_song_id=interaction.song_id,
        )
    )

    features = build_training_features(
        song=interaction.song,
        interaction=interaction,
        user_profile=user_profile,
    )

    features["user_id"] = interaction.user_id
    features["song_id"] = interaction.song.id
    features["target"] = 0

    return features


def build_negative_row(
    user_id,
    song,
):

    user_profile = (
        get_user_taste_profile(
            user_id=user_id
        )
    )

    features = build_training_features(
        song=song,
        interaction=None,
        user_profile=user_profile,
    )

    features["user_id"] = user_id
    features["song_id"] = song.id
    features["target"] = 0

    return features


def build_training_dataset(
    negative_samples_per_positive=(
        NEGATIVE_SAMPLES_PER_POSITIVE
    ),
):

    rng = random.Random(
        RANDOM_SEED
    )

    positives = list(
        get_positive_interactions()
    )

    real_negatives = list(
        get_negative_interactions()
    )

    if not positives:
        return []

    all_song_ids = list(
        Songs.objects
        .filter(is_published=True)
        .values_list(
            "id",
            flat=True,
        )
    )

    songs = {
        song.id: song
        for song in (
            Songs.objects
            .filter(
                id__in=all_song_ids,
                is_published=True,
            )
        )
    }

    dataset = []

    for interaction in positives:
        dataset.append(
            build_positive_row(
                interaction
            )
        )

    for interaction in real_negatives:
        dataset.append(
            build_real_negative_row(
                interaction
            )
        )

    for interaction in positives:

        negative_song_ids = (
            get_negative_songs(
                user_id=interaction.user_id,
                all_song_ids=all_song_ids,
                count=negative_samples_per_positive,
                rng=rng,
            )
        )

        for song_id in negative_song_ids:

            song = songs.get(song_id)

            if song is None:
                continue

            dataset.append(
                build_negative_row(
                    user_id=interaction.user_id,
                    song=song,
                )
            )

    return dataset


def get_training_features():
    return get_feature_names()


def get_training_data_and_labels(
    negative_samples_per_positive=(
        NEGATIVE_SAMPLES_PER_POSITIVE
    ),
):

    dataset = build_training_dataset(
        negative_samples_per_positive=(
            negative_samples_per_positive
        )
    )

    feature_names = (
        get_training_features()
    )

    X = [
        [
            row[feature]
            for feature in feature_names
        ]
        for row in dataset
    ]

    y = [
        row["target"]
        for row in dataset
    ]

    return X, y


def print_dataset_summary(dataset):

    total = len(dataset)

    positives = sum(
        row["target"] == 1
        for row in dataset
    )

    negatives = sum(
        row["target"] == 0
        for row in dataset
    )

    users = len(
        {
            row["user_id"]
            for row in dataset
        }
    )

    songs = len(
        {
            row["song_id"]
            for row in dataset
        }
    )

    print(
        "\n========== DATASET SUMMARY =========="
    )

    print(
        f"Total samples:       {total}"
    )

    print(
        f"Positive samples:    {positives}"
    )

    print(
        f"Negative samples:    {negatives}"
    )

    print(
        f"Users:               {users}"
    )

    print(
        f"Songs:               {songs}"
    )

    if total:
        print(
            f"Positive ratio:      "
            f"{positives / total:.2%}"
        )

    print(
        "=====================================\n"
    )


def print_interaction_target_summary():

    interactions = list(
        UserSongInteraction.objects.all()
    )

    positive_count = 0
    negative_count = 0

    for interaction in interactions:

        target = get_target(
            interaction
        )

        if target == 1:
            positive_count += 1
        else:
            negative_count += 1

    print(
        "\n======= INTERACTION TARGET SUMMARY ======="
    )

    print(
        f"Total interactions: {len(interactions)}"
    )

    print(
        f"Positive:           {positive_count}"
    )

    print(
        f"Negative:           {negative_count}"
    )

    if interactions:

        print(
            f"Positive ratio:     "
            f"{positive_count / len(interactions):.2%}"
        )

    print(
        "==========================================\n"
    )