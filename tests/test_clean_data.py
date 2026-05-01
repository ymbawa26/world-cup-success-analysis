from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from clean_data import clean_international_results, standardize_team_name


def test_team_names_are_standardized():
    assert standardize_team_name("USA") == "United States"
    assert standardize_team_name("Korea Republic") == "South Korea"
    assert standardize_team_name("Czechia") == "Czech Republic"


def test_dates_goals_missing_values_and_outcomes_are_handled():
    raw = pd.DataFrame(
        {
            "date": ["2022-01-01", "bad-date"],
            "home_team": ["USA", "France"],
            "away_team": ["Mexico", "Spain"],
            "home_score": ["2", None],
            "away_score": ["0", "1"],
            "tournament": ["Friendly", "Friendly"],
            "city": ["A", "B"],
            "country": ["USA", "France"],
            "neutral": [False, False],
        }
    )
    clean = clean_international_results(raw)
    assert len(clean) == 1
    assert clean.loc[0, "date"] == pd.Timestamp("2022-01-01")
    assert clean.loc[0, "home_score"] == 2
    assert clean.loc[0, "home_outcome"] == "win"
