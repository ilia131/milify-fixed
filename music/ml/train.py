from pathlib import Path
import os
import sys


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


# =========================================================
# DJANGO SETUP
# =========================================================

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "backend.settings",
)

import django

django.setup()


# =========================================================
# THIRD-PARTY
# =========================================================

import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


# =========================================================
# PROJECT IMPORTS
# =========================================================

from music.ml.training_dataset import (
    build_training_dataset,
    get_training_features,
)
# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = (
    PROJECT_ROOT
    / "ml-service"
    / "models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

MODEL_PATH = (
    MODEL_DIR
    / "recommender.joblib"
)


# =========================================================
# CONFIGURATION
# =========================================================

MIN_SAMPLES = 20
MIN_POSITIVE_SAMPLES = 5
MIN_NEGATIVE_SAMPLES = 5

TEST_SIZE = 0.2
RANDOM_STATE = 42


# =========================================================
# DJANGO SETUP
# =========================================================

def setup_django():
    """
    Initialize Django so the ML training script
    can access Django models and database.
    """

    project_root = str(PROJECT_ROOT)

    if project_root not in sys.path:
        sys.path.insert(
            0,
            project_root,
        )

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "backend.settings",
    )

    import django

    django.setup()


# =========================================================
# LOAD DATASET
# =========================================================

def load_dataset():
    """
    Build the training dataset from Django.
    """

    print(
        "Initializing Django..."
    )

    setup_django()

    print(
        "Building training dataset..."
    )

    dataset = build_training_dataset()

    return dataset


# =========================================================
# DATASET → DATAFRAME
# =========================================================

def dataset_to_dataframe(
    dataset,
    feature_names,
):
    """
    Convert training dataset into pandas DataFrame.
    """

    if not dataset:
        return pd.DataFrame()

    dataframe = pd.DataFrame(
        dataset
    )

    required_columns = (
        feature_names
        + ["target"]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing columns:\n"
            + "\n".join(
                f"- {column}"
                for column in missing_columns
            )
        )

    dataframe = dataframe[
        required_columns
    ].copy()

    dataframe = dataframe.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    dataframe = dataframe.fillna(0)

    return dataframe


# =========================================================
# VALIDATE DATASET
# =========================================================

def validate_dataset(
    dataframe,
    feature_names,
):
    """
    Validate that the dataset contains enough
    positive and negative samples.
    """

    if dataframe.empty:
        raise ValueError(
            "Training dataset is empty."
        )

    total_samples = len(
        dataframe
    )

    positive_samples = int(
        (
            dataframe["target"] == 1
        ).sum()
    )

    negative_samples = int(
        (
            dataframe["target"] == 0
        ).sum()
    )

    print(
        "\n========== TRAINING DATA =========="
    )

    print(
        f"Total samples:     {total_samples}"
    )

    print(
        f"Positive samples:  {positive_samples}"
    )

    print(
        f"Negative samples:  {negative_samples}"
    )

    print(
        f"Features:          {len(feature_names)}"
    )

    print(
        "===================================\n"
    )

    if total_samples < MIN_SAMPLES:
        raise ValueError(
            f"Not enough samples. "
            f"Need at least {MIN_SAMPLES}, "
            f"got {total_samples}."
        )

    if positive_samples < MIN_POSITIVE_SAMPLES:
        raise ValueError(
            f"Not enough positive samples. "
            f"Need at least "
            f"{MIN_POSITIVE_SAMPLES}, "
            f"got {positive_samples}."
        )

    if negative_samples < MIN_NEGATIVE_SAMPLES:
        raise ValueError(
            f"Not enough negative samples. "
            f"Need at least "
            f"{MIN_NEGATIVE_SAMPLES}, "
            f"got {negative_samples}."
        )


# =========================================================
# TRAIN MODEL
# =========================================================

def train_model(
    dataframe,
    feature_names,
):
    """
    Train LightGBM binary classifier.
    """

    X = dataframe[
        feature_names
    ]

    y = dataframe[
        "target"
    ]

    print(
        "\nSplitting dataset..."
    )

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=y,
        )
    )

    print(
        f"Training samples:   {len(X_train)}"
    )

    print(
        f"Validation samples: {len(X_test)}"
    )

    print(
        f"Training features:  {len(feature_names)}"
    )

    print(
        "\nTraining LightGBM...\n"
    )

    model = lgb.LGBMClassifier(
        objective="binary",

        n_estimators=200,

        learning_rate=0.05,

        num_leaves=15,

        max_depth=5,

        min_child_samples=5,

        subsample=0.8,

        colsample_bytree=0.8,

        random_state=RANDOM_STATE,

        n_jobs=-1,

        verbosity=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    # =====================================================
    # PREDICTIONS
    # =====================================================

    predictions = model.predict(
        X_test
    )

    probabilities = (
        model
        .predict_proba(X_test)[:, 1]
    )

    # =====================================================
    # METRICS
    # =====================================================

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    try:
        auc = roc_auc_score(
            y_test,
            probabilities,
        )
    except ValueError:
        auc = None

    print(
        "\n========== MODEL METRICS =========="
    )

    print(
        f"Accuracy:   {accuracy:.4f}"
    )

    print(
        f"Precision:  {precision:.4f}"
    )

    print(
        f"Recall:     {recall:.4f}"
    )

    if auc is not None:
        print(
            f"ROC-AUC:    {auc:.4f}"
        )
    else:
        print(
            "ROC-AUC:    unavailable"
        )

    print(
        "===================================\n"
    )

    return model


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

def print_feature_importance(
    model,
    feature_names,
):
    """
    Print LightGBM feature importance.
    """

    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": (
                model.feature_importances_
            ),
        }
    )

    importance = (
        importance
        .sort_values(
            "importance",
            ascending=False,
        )
    )

    print(
        "\n========== FEATURE IMPORTANCE =========="
    )

    print(
        importance.to_string(
            index=False
        )
    )

    print(
        "========================================\n"
    )


# =========================================================
# SAVE MODEL
# =========================================================

def save_model(
    model,
    feature_names,
):
    """
    Save trained LightGBM model.

    The feature names are saved alongside the model
    so we can verify compatibility later.
    """

    model_package = {
        "model": model,
        "feature_names": feature_names,
        "version": 2,
    }

    joblib.dump(
        model_package,
        MODEL_PATH,
    )

    print(
        f"Model saved to:\n{MODEL_PATH}"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\n========================================"
    )

    print(
        "       MILIFY LIGHTGBM TRAINING"
    )

    print(
        "========================================\n"
    )

    # -----------------------------------------------------
    # Feature names
    # -----------------------------------------------------

    feature_names = (
        get_training_features()
    )

    print(
        f"Feature count: {len(feature_names)}"
    )

    print(
        "\nFeatures:"
    )

    for index, feature in enumerate(
        feature_names,
        start=1,
    ):
        print(
            f"{index:02d}. {feature}"
        )

    # -----------------------------------------------------
    # Dataset
    # -----------------------------------------------------

    print(
        "\nLoading dataset..."
    )

    dataset = load_dataset()

    print(
        f"Raw dataset rows: {len(dataset)}"
    )

    # -----------------------------------------------------
    # DataFrame
    # -----------------------------------------------------

    dataframe = dataset_to_dataframe(
        dataset=dataset,
        feature_names=feature_names,
    )

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    validate_dataset(
        dataframe=dataframe,
        feature_names=feature_names,
    )

    # -----------------------------------------------------
    # Training
    # -----------------------------------------------------

    model = train_model(
        dataframe=dataframe,
        feature_names=feature_names,
    )

    # -----------------------------------------------------
    # Importance
    # -----------------------------------------------------

    print_feature_importance(
        model=model,
        feature_names=feature_names,
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    save_model(
        model=model,
        feature_names=feature_names,
    )

    print(
        "\nTraining completed successfully. 🚀\n"
    )


if __name__ == "__main__":
    main()