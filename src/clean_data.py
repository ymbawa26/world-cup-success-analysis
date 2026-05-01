"""Clean raw World Cup data and engineer analysis features."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from load_data import PROJECT_ROOT, RAW_DIR, ensure_raw_data, load_all_raw


PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

TEAM_ALIASES = {
    "USA": "United States",
    "U.S.": "United States",
    "US": "United States",
    "Korea Republic": "South Korea",
    "Republic of Korea": "South Korea",
    "Czechia": "Czech Republic",
    "Czech Republic": "Czech Republic",
    "Türkiye": "Turkey",
    "Turkiye": "Turkey",
    "IR Iran": "Iran",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Cabo Verde": "Cape Verde",
    "Congo DR": "DR Congo",
    "Democratic Republic of the Congo": "DR Congo",
    "Zaire": "DR Congo",
    "Bosnia-Herzegovina": "Bosnia & Herzegovina",
    "Bosnia and Herzegovina": "Bosnia & Herzegovina",
    "Dutch East Indies": "Indonesia",
}

STAGE_SCORE = {
    "group stage": 1,
    "round of 16": 2,
    "second group stage": 2,
    "quarter-final": 3,
    "quarter-finals": 3,
    "quater-finals": 3,
    "semi-finals": 4,
    "third-place match": 4,
    "final round": 5,
    "final": 5,
    "runners-up": 5,
    "third place": 4,
    "fourth place": 4,
    "champions": 6,
}

CONFED_2026 = {
    "Algeria": "CAF",
    "Argentina": "CONMEBOL",
    "Australia": "AFC",
    "Austria": "UEFA",
    "Belgium": "UEFA",
    "Bosnia & Herzegovina": "UEFA",
    "Brazil": "CONMEBOL",
    "Canada": "CONCACAF",
    "Cape Verde": "CAF",
    "Colombia": "CONMEBOL",
    "Croatia": "UEFA",
    "Curacao": "CONCACAF",
    "Czech Republic": "UEFA",
    "DR Congo": "CAF",
    "Ecuador": "CONMEBOL",
    "Egypt": "CAF",
    "England": "UEFA",
    "France": "UEFA",
    "Germany": "UEFA",
    "Ghana": "CAF",
    "Haiti": "CONCACAF",
    "Iran": "AFC",
    "Iraq": "AFC",
    "Ivory Coast": "CAF",
    "Japan": "AFC",
    "Jordan": "AFC",
    "Mexico": "CONCACAF",
    "Morocco": "CAF",
    "Netherlands": "UEFA",
    "New Zealand": "OFC",
    "Norway": "UEFA",
    "Panama": "CONCACAF",
    "Paraguay": "CONMEBOL",
    "Portugal": "UEFA",
    "Qatar": "AFC",
    "Saudi Arabia": "AFC",
    "Scotland": "UEFA",
    "Senegal": "CAF",
    "South Africa": "CAF",
    "South Korea": "AFC",
    "Spain": "UEFA",
    "Sweden": "UEFA",
    "Switzerland": "UEFA",
    "Tunisia": "CAF",
    "Turkey": "UEFA",
    "United States": "CONCACAF",
    "Uruguay": "CONMEBOL",
    "Uzbekistan": "AFC",
}


def standardize_team_name(name: object) -> object:
    """Standardize team names across sources while preserving missing values."""
    if pd.isna(name):
        return name
    cleaned = str(name).strip()
    cleaned = cleaned.replace("\ufeff", "")
    return TEAM_ALIASES.get(cleaned, cleaned)


def parse_dates(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Parse date columns with validation-friendly coercion."""
    out = frame.copy()
    for column in columns:
        out[column] = pd.to_datetime(out[column], errors="coerce")
    return out


def clean_team_appearances(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean the team-match-level World Cup table."""
    df = raw.copy()
    df = df[df["tournament_name"].str.contains("Men's World Cup", na=False)].copy()
    df = parse_dates(df, ["match_date"])
    for column in ["goals_for", "goals_against", "goal_differential", "win", "lose", "draw"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    for column in ["team_name", "opponent_name", "country_name"]:
        df[column] = df[column].map(standardize_team_name)
    df["year"] = df["tournament_id"].str.extract(r"(\d{4})").astype(int)
    df["outcome"] = np.select(
        [df["win"].eq(1), df["lose"].eq(1), df["draw"].eq(1)],
        ["win", "loss", "draw"],
        default="unknown",
    )
    df = df.drop_duplicates(subset=["match_id", "team_name"])
    if (df[["goals_for", "goals_against"]] < 0).any().any():
        raise ValueError("World Cup appearances contain negative goal values.")
    return df


def clean_matches(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean the match-level World Cup table."""
    df = raw.copy()
    df = df[df["tournament_name"].str.contains("Men's World Cup", na=False)].copy()
    df = parse_dates(df, ["match_date"])
    for column in ["home_team_score", "away_team_score"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    for column in ["home_team_name", "away_team_name", "country_name"]:
        df[column] = df[column].map(standardize_team_name)
    df["year"] = df["tournament_id"].str.extract(r"(\d{4})").astype(int)
    df = df.drop_duplicates(subset=["match_id"])
    return df


def clean_international_results(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean international match results and remove fixtures without scores."""
    df = raw.copy()
    df = parse_dates(df, ["date"])
    df["home_score"] = pd.to_numeric(df["home_score"], errors="coerce")
    df["away_score"] = pd.to_numeric(df["away_score"], errors="coerce")
    df["home_team"] = df["home_team"].map(standardize_team_name)
    df["away_team"] = df["away_team"].map(standardize_team_name)
    df["country"] = df["country"].map(standardize_team_name)
    df = df.drop_duplicates()
    df = df.dropna(subset=["date", "home_team", "away_team", "home_score", "away_score"])
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    df["home_outcome"] = np.select(
        [df["home_score"].gt(df["away_score"]), df["home_score"].lt(df["away_score"])],
        ["win", "loss"],
        default="draw",
    )
    return df


def team_long_results(results: pd.DataFrame) -> pd.DataFrame:
    """Convert international results into one row per team per match."""
    home = results.rename(
        columns={
            "home_team": "team_name",
            "away_team": "opponent_name",
            "home_score": "goals_for",
            "away_score": "goals_against",
        }
    ).copy()
    home["is_home"] = True
    away = results.rename(
        columns={
            "away_team": "team_name",
            "home_team": "opponent_name",
            "away_score": "goals_for",
            "home_score": "goals_against",
        }
    ).copy()
    away["is_home"] = False
    keep = ["date", "team_name", "opponent_name", "goals_for", "goals_against", "tournament", "country", "neutral", "is_home"]
    long = pd.concat([home[keep], away[keep]], ignore_index=True)
    long["win"] = (long["goals_for"] > long["goals_against"]).astype(int)
    long["loss"] = (long["goals_for"] < long["goals_against"]).astype(int)
    long["draw"] = (long["goals_for"] == long["goals_against"]).astype(int)
    long["points"] = long["win"] * 3 + long["draw"]
    long["goal_difference"] = long["goals_for"] - long["goals_against"]
    return long


def prepare_dimension_tables(raw: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    tournaments = raw["fjelstul_tournaments.csv"].copy()
    tournaments = tournaments[tournaments["tournament_name"].str.contains("Men's World Cup", na=False)].copy()
    tournaments = parse_dates(tournaments, ["start_date", "end_date"])
    tournaments["year"] = tournaments["year"].astype(int)

    teams = raw["fjelstul_teams.csv"].copy()
    teams["team_name"] = teams["team_name"].map(standardize_team_name)
    teams = teams[["team_id", "team_name", "team_code", "region_name", "confederation_code"]].drop_duplicates("team_name")

    host_countries = raw["fjelstul_host_countries.csv"].copy()
    host_countries["team_name"] = host_countries["team_name"].map(standardize_team_name)
    host_countries["year"] = host_countries["tournament_id"].str.extract(r"(\d{4})").astype(int)

    standings = raw["fjelstul_tournament_standings.csv"].copy()
    standings["team_name"] = standings["team_name"].map(standardize_team_name)
    standings["position"] = pd.to_numeric(standings["position"], errors="coerce")
    standings["year"] = standings["tournament_id"].str.extract(r"(\d{4})").astype(int)

    qualified = raw["fjelstul_qualified_teams.csv"].copy()
    qualified["team_name"] = qualified["team_name"].map(standardize_team_name)
    qualified["year"] = qualified["tournament_id"].str.extract(r"(\d{4})").astype(int)
    qualified["stage_score_from_label"] = qualified["performance"].map(STAGE_SCORE).fillna(1).astype(int)

    return {
        "tournaments": tournaments,
        "teams": teams,
        "host_countries": host_countries,
        "standings": standings,
        "qualified": qualified,
    }


def engineer_pre_tournament_form(long_results: pd.DataFrame, teams_years: pd.DataFrame, tournaments: pd.DataFrame) -> pd.DataFrame:
    """Calculate one-year form before each World Cup starts, excluding World Cup matches."""
    starts = tournaments[["tournament_id", "year", "start_date"]]
    base = teams_years[["tournament_id", "year", "team_name"]].merge(starts, on=["tournament_id", "year"], how="left")
    rows = []
    non_wc = long_results[~long_results["tournament"].eq("FIFA World Cup")].copy()
    for row in base.itertuples(index=False):
        window_start = row.start_date - pd.Timedelta(days=365)
        subset = non_wc[
            (non_wc["team_name"].eq(row.team_name))
            & (non_wc["date"] >= window_start)
            & (non_wc["date"] < row.start_date)
        ]
        matches = len(subset)
        rows.append(
            {
                "tournament_id": row.tournament_id,
                "year": row.year,
                "team_name": row.team_name,
                "pre_wc_matches": matches,
                "pre_wc_points_per_match": float(subset["points"].mean()) if matches else np.nan,
                "pre_wc_win_rate": float(subset["win"].mean()) if matches else np.nan,
                "pre_wc_goal_diff_per_match": float(subset["goal_difference"].mean()) if matches else np.nan,
                "pre_wc_goals_for_per_match": float(subset["goals_for"].mean()) if matches else np.nan,
                "pre_wc_goals_against_per_match": float(subset["goals_against"].mean()) if matches else np.nan,
            }
        )
    return pd.DataFrame(rows)


def engineer_team_tournament_features(
    appearances: pd.DataFrame,
    dimensions: dict[str, pd.DataFrame],
    form: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate match-level data into one team-tournament analytical table."""
    agg = (
        appearances.groupby(["tournament_id", "year", "team_name"], as_index=False)
        .agg(
            matches=("match_id", "nunique"),
            wins=("win", "sum"),
            losses=("lose", "sum"),
            draws=("draw", "sum"),
            goals_for=("goals_for", "sum"),
            goals_against=("goals_against", "sum"),
            goal_difference=("goal_differential", "sum"),
            knockout_matches=("knockout_stage", "sum"),
        )
    )
    agg["win_rate"] = agg["wins"] / agg["matches"]
    agg["goals_for_per_match"] = agg["goals_for"] / agg["matches"]
    agg["goals_against_per_match"] = agg["goals_against"] / agg["matches"]

    teams = dimensions["teams"]
    host = dimensions["host_countries"][["tournament_id", "team_name"]].assign(is_host=1)
    standings = dimensions["standings"][["tournament_id", "team_name", "position"]]
    qualified = dimensions["qualified"][["tournament_id", "team_name", "performance", "stage_score_from_label"]]

    features = agg.merge(teams, on="team_name", how="left")
    features = features.merge(host, on=["tournament_id", "team_name"], how="left")
    features["is_host"] = features["is_host"].fillna(0).astype(int)
    features = features.merge(standings, on=["tournament_id", "team_name"], how="left")
    features = features.merge(qualified, on=["tournament_id", "team_name"], how="left")
    features["stage_score"] = features["stage_score_from_label"].fillna(1).astype(int)
    features.loc[features["position"].eq(1), "stage_score"] = 6
    features.loc[features["position"].eq(2), "stage_score"] = 5
    features.loc[features["position"].isin([3, 4]), "stage_score"] = 4
    features["stage_reached"] = features["stage_score"].map(
        {1: "Group stage", 2: "Round of 16 / second group", 3: "Quarter-finals", 4: "Semi-finals/top four", 5: "Final", 6: "Champion"}
    )
    features["champion"] = features["position"].eq(1).astype(int)
    features["finalist"] = features["position"].isin([1, 2]).astype(int)
    features["semifinalist"] = features["position"].isin([1, 2, 3, 4]).astype(int)
    features["reached_knockout"] = ((features["knockout_matches"] > 0) | (features["stage_score"] > 1)).astype(int)
    features = features.merge(form, on=["tournament_id", "year", "team_name"], how="left")
    features = features.sort_values(["team_name", "year"])
    features["historical_tournaments_before"] = features.groupby("team_name").cumcount()
    features["historical_matches_before"] = features.groupby("team_name")["matches"].cumsum() - features["matches"]
    features["historical_wins_before"] = features.groupby("team_name")["wins"].cumsum() - features["wins"]
    features["historical_best_stage_before"] = (
        features.groupby("team_name")["stage_score"].cummax().shift(fill_value=0)
    )
    features["historical_best_stage_before"] = features.groupby("team_name")["historical_best_stage_before"].transform(lambda s: s.ffill().fillna(0))
    return features


def parse_2026_groups(path: Path = RAW_DIR / "openfootball_2026_cup.txt") -> pd.DataFrame:
    """Parse the OpenFootball 2026 group listing into a structured table."""
    text = path.read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        if not line.startswith("Group ") or "|" not in line:
            continue
        group, teams_text = line.split("|", 1)
        group_name = group.replace("Group", "").strip()
        teams = [standardize_team_name(part.strip()) for part in re.split(r"\t+|\s{2,}", teams_text.strip()) if part.strip()]
        for team in teams:
            rows.append({"year": 2026, "group_name": group_name, "team_name": team, "confederation_code": CONFED_2026.get(team)})
    frame = pd.DataFrame(rows)
    if len(frame) != 48:
        raise ValueError(f"Expected 48 teams from OpenFootball 2026 file, found {len(frame)}")
    return frame


def build_2026_preview(features: pd.DataFrame, long_results: pd.DataFrame, groups_2026: pd.DataFrame) -> pd.DataFrame:
    """Create a no-results preview table for the 48-team 2026 field."""
    historical = (
        features.sort_values(["team_name", "year"])
        .groupby("team_name", as_index=False)
        .agg(
            prior_world_cups=("year", "nunique"),
            prior_matches=("matches", "sum"),
            prior_wins=("wins", "sum"),
            prior_titles=("champion", "sum"),
            prior_finals=("finalist", "sum"),
            prior_semifinals=("semifinalist", "sum"),
            best_stage_score=("stage_score", "max"),
            avg_goal_difference=("goal_difference", "mean"),
        )
    )
    starts = pd.DataFrame({"tournament_id": ["WC-2026"] * len(groups_2026), "year": [2026] * len(groups_2026), "team_name": groups_2026["team_name"]})
    tournaments = pd.DataFrame({"tournament_id": ["WC-2026"], "year": [2026], "start_date": [pd.Timestamp("2026-06-11")]})
    form_2026 = engineer_pre_tournament_form(long_results, starts, tournaments)
    preview = groups_2026.merge(historical, on="team_name", how="left").merge(
        form_2026.drop(columns=["tournament_id", "year"]), on="team_name", how="left"
    )
    for column in ["prior_world_cups", "prior_matches", "prior_wins", "prior_titles", "prior_finals", "prior_semifinals", "best_stage_score"]:
        preview[column] = preview[column].fillna(0).astype(int)
    return preview


def build_processed_data() -> dict[str, pd.DataFrame]:
    """Run the complete cleaning and feature engineering pipeline."""
    ensure_raw_data()
    raw = load_all_raw()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    appearances = clean_team_appearances(raw["fjelstul_team_appearances.csv"])
    matches = clean_matches(raw["fjelstul_matches.csv"])
    results = clean_international_results(raw["international_results.csv"])
    long_results = team_long_results(results)
    dimensions = prepare_dimension_tables(raw)

    form = engineer_pre_tournament_form(
        long_results,
        dimensions["qualified"][["tournament_id", "year", "team_name"]],
        dimensions["tournaments"],
    )
    features = engineer_team_tournament_features(appearances, dimensions, form)
    groups_2026 = parse_2026_groups()
    preview_2026 = build_2026_preview(features, long_results, groups_2026)

    outputs = {
        "matches_clean.csv": matches,
        "team_appearances_clean.csv": appearances,
        "international_results_clean.csv": results,
        "team_results_long.csv": long_results,
        "pre_tournament_form.csv": form,
        "team_tournament_features.csv": features,
        "world_cup_2026_qualified_teams.csv": groups_2026,
        "world_cup_2026_team_preview.csv": preview_2026,
    }
    for filename, frame in outputs.items():
        frame.to_csv(PROCESSED_DIR / filename, index=False)
    return outputs


if __name__ == "__main__":
    output_frames = build_processed_data()
    print(f"Processed {len(output_frames)} datasets into {PROCESSED_DIR}")
