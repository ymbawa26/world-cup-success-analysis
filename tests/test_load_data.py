from pathlib import Path

import pandas as pd

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from load_data import RAW_DIR, load_csv, validate_required_columns


def test_raw_files_load_and_are_not_empty():
    frame = load_csv("fjelstul_team_appearances.csv", RAW_DIR)
    assert not frame.empty


def test_required_columns_exist():
    frame = load_csv("fjelstul_team_appearances.csv", RAW_DIR)
    validate_required_columns(frame, "fjelstul_team_appearances.csv")


def test_duplicate_rows_can_be_detected_and_removed():
    data = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    assert data.duplicated().sum() == 1
    assert len(data.drop_duplicates()) == 2
