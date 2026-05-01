"""Data loading utilities for the World Cup success analysis project."""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

RAW_SOURCES = {
    "fjelstul_matches.csv": "https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/matches.csv",
    "fjelstul_team_appearances.csv": "https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/team_appearances.csv",
    "fjelstul_tournaments.csv": "https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/tournaments.csv",
    "fjelstul_qualified_teams.csv": "https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/qualified_teams.csv",
    "fjelstul_teams.csv": "https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/teams.csv",
    "fjelstul_tournament_standings.csv": "https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/tournament_standings.csv",
    "fjelstul_host_countries.csv": "https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/host_countries.csv",
    "international_results.csv": "https://raw.githubusercontent.com/martj42/international_results/master/results.csv",
    "openfootball_2026_cup.txt": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup.txt",
}

REQUIRED_COLUMNS = {
    "fjelstul_team_appearances.csv": {
        "tournament_id",
        "tournament_name",
        "match_id",
        "stage_name",
        "match_date",
        "team_name",
        "opponent_name",
        "goals_for",
        "goals_against",
        "win",
        "lose",
        "draw",
    },
    "fjelstul_matches.csv": {
        "tournament_id",
        "match_id",
        "stage_name",
        "match_date",
        "home_team_name",
        "away_team_name",
        "home_team_score",
        "away_team_score",
    },
    "international_results.csv": {
        "date",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "tournament",
        "country",
        "neutral",
    },
}


def ensure_raw_data(raw_dir: Path = RAW_DIR) -> list[Path]:
    """Download raw public files that are not already present."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[Path] = []
    for filename, url in RAW_SOURCES.items():
        destination = raw_dir / filename
        if not destination.exists() or destination.stat().st_size == 0:
            urlretrieve(url, destination)
        downloaded.append(destination)
    return downloaded


def load_csv(filename: str, raw_dir: Path = RAW_DIR, **kwargs) -> pd.DataFrame:
    """Load a raw CSV file and validate that it is not empty."""
    path = raw_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing raw data file: {path}")
    frame = pd.read_csv(path, **kwargs)
    if frame.empty:
        raise ValueError(f"Raw data file loaded with zero rows: {path}")
    return frame


def validate_required_columns(frame: pd.DataFrame, filename: str) -> None:
    """Raise a clear error when a source file is missing required fields."""
    required = REQUIRED_COLUMNS.get(filename, set())
    missing = required.difference(frame.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"{filename} is missing required columns: {missing_text}")


def load_all_raw(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    """Load all CSV sources used by the project."""
    ensure_raw_data(raw_dir)
    data: dict[str, pd.DataFrame] = {}
    for filename in RAW_SOURCES:
        path = raw_dir / filename
        if path.suffix == ".txt":
            continue
        frame = load_csv(filename, raw_dir)
        validate_required_columns(frame, filename)
        data[filename] = frame
    return data


if __name__ == "__main__":
    files = ensure_raw_data()
    print(f"Raw data ready: {len(files)} files in {RAW_DIR}")
