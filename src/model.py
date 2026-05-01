"""Leakage-safe baseline model for reaching the World Cup semifinals."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from clean_data import PROJECT_ROOT, build_processed_data


PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FEATURE_COLUMNS = [
    "is_host",
    "historical_tournaments_before",
    "historical_matches_before",
    "historical_wins_before",
    "historical_best_stage_before",
    "pre_wc_points_per_match",
    "pre_wc_win_rate",
    "pre_wc_goal_diff_per_match",
    "confederation_code",
]


def train_baseline_model() -> dict[str, Path | float]:
    """Train a simple semifinal model using a split by tournament year."""
    if not (PROCESSED_DIR / "team_tournament_features.csv").exists():
        build_processed_data()
    data = pd.read_csv(PROCESSED_DIR / "team_tournament_features.csv")
    model_data = data[data["year"] >= 1966].copy()
    model_data["confederation_code"] = model_data["confederation_code"].fillna("Unknown")

    train = model_data[model_data["year"] <= 2006]
    test = model_data[model_data["year"] >= 2010]
    numeric_features = [column for column in FEATURE_COLUMNS if column != "confederation_code"]
    categorical_features = ["confederation_code"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_features),
            ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical_features),
        ]
    )
    model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
        ]
    )
    model.fit(train[FEATURE_COLUMNS], train["semifinalist"])
    probabilities = model.predict_proba(test[FEATURE_COLUMNS])[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    accuracy = accuracy_score(test["semifinalist"], predictions)
    matrix = confusion_matrix(test["semifinalist"], predictions, labels=[0, 1])

    scored = test[["year", "team_name", "semifinalist", "stage_reached"]].copy()
    scored["predicted_semifinalist"] = predictions
    scored["semifinal_probability"] = probabilities
    scored = scored.sort_values(["year", "semifinal_probability"], ascending=[True, False])

    feature_names = numeric_features + list(
        model.named_steps["preprocess"].named_transformers_["categorical"].named_steps["onehot"].get_feature_names_out(categorical_features)
    )
    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "coefficient": model.named_steps["classifier"].coef_[0],
        }
    ).sort_values("coefficient", key=lambda s: s.abs(), ascending=False)

    scored_path = PROCESSED_DIR / "baseline_model_predictions.csv"
    importance_path = PROCESSED_DIR / "baseline_model_feature_importance.csv"
    matrix_path = PROCESSED_DIR / "baseline_model_confusion_matrix.csv"
    summary_path = PROCESSED_DIR / "baseline_model_summary.csv"
    scored.to_csv(scored_path, index=False)
    importance.to_csv(importance_path, index=False)
    pd.DataFrame(matrix, index=["actual_not_semifinal", "actual_semifinal"], columns=["pred_not_semifinal", "pred_semifinal"]).to_csv(matrix_path)
    pd.DataFrame(
        [{"target": "semifinalist", "train_years": "1966-2006", "test_years": "2010-2022", "accuracy": accuracy}]
    ).to_csv(summary_path, index=False)
    return {
        "accuracy": float(accuracy),
        "scored_path": scored_path,
        "importance_path": importance_path,
        "matrix_path": matrix_path,
        "summary_path": summary_path,
    }


if __name__ == "__main__":
    results = train_baseline_model()
    print(f"Baseline model accuracy: {results['accuracy']:.3f}")
