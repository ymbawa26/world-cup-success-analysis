from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from clean_data import build_processed_data, engineer_pre_tournament_form, parse_2026_groups


def test_host_advantage_flag_and_labels_are_present():
    outputs = build_processed_data()
    features = outputs["team_tournament_features.csv"]
    uruguay_1930 = features[(features["year"].eq(1930)) & (features["team_name"].eq("Uruguay"))].iloc[0]
    assert uruguay_1930["is_host"] == 1
    assert uruguay_1930["champion"] == 1
    assert uruguay_1930["finalist"] == 1
    assert uruguay_1930["semifinalist"] == 1


def test_historical_experience_uses_only_past_tournaments():
    outputs = build_processed_data()
    brazil = outputs["team_tournament_features.csv"].query("team_name == 'Brazil'").sort_values("year")
    first = brazil.iloc[0]
    second = brazil.iloc[1]
    assert first["historical_tournaments_before"] == 0
    assert second["historical_tournaments_before"] == 1
    assert second["historical_matches_before"] == first["matches"]


def test_pre_tournament_form_excludes_world_cup_results():
    long_results = pd.DataFrame(
        {
            "date": pd.to_datetime(["2022-06-01", "2022-11-22"]),
            "team_name": ["Example", "Example"],
            "opponent_name": ["A", "B"],
            "goals_for": [1, 5],
            "goals_against": [0, 0],
            "tournament": ["Friendly", "FIFA World Cup"],
            "country": ["X", "Y"],
            "neutral": [True, True],
            "is_home": [False, False],
            "win": [1, 1],
            "loss": [0, 0],
            "draw": [0, 0],
            "points": [3, 3],
            "goal_difference": [1, 5],
        }
    )
    teams = pd.DataFrame({"tournament_id": ["WC-2022"], "year": [2022], "team_name": ["Example"]})
    tournaments = pd.DataFrame({"tournament_id": ["WC-2022"], "year": [2022], "start_date": [pd.Timestamp("2022-11-20")]})
    form = engineer_pre_tournament_form(long_results, teams, tournaments)
    assert form.loc[0, "pre_wc_matches"] == 1
    assert form.loc[0, "pre_wc_goal_diff_per_match"] == 1


def test_2026_field_has_48_teams():
    groups = parse_2026_groups()
    assert len(groups) == 48
    assert groups["team_name"].nunique() == 48
