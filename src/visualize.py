"""Generate static and interactive charts for the World Cup analysis."""

from __future__ import annotations

import os
from pathlib import Path

from clean_data import PROJECT_ROOT, build_processed_data
from run_sql_analysis import run_sql_scripts

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CHART_DIR = PROJECT_ROOT / "charts"
MPLCONFIG_DIR = PROJECT_ROOT / ".mplconfig"
MPLCONFIG_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIG_DIR))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px


PALETTE = {
    "blue": "#1F6FEB",
    "green": "#2DA44E",
    "red": "#CF222E",
    "gold": "#B08800",
    "gray": "#57606A",
}


def _load_features() -> pd.DataFrame:
    if not (PROCESSED_DIR / "team_tournament_features.csv").exists():
        build_processed_data()
    return pd.read_csv(PROCESSED_DIR / "team_tournament_features.csv")


def _save_bar(frame: pd.DataFrame, x: str, y: str, title: str, ylabel: str, filename: str, color: str = "blue") -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    frame.plot(kind="barh", x=x, y=y, ax=ax, color=PALETTE[color], legend=False)
    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xlabel(ylabel)
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(CHART_DIR / filename, dpi=180)
    plt.close(fig)


def generate_charts() -> list[Path]:
    """Create all portfolio charts and a short interpretation file."""
    build_processed_data()
    run_sql_scripts()
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    features = _load_features()
    preview_2026 = pd.read_csv(PROCESSED_DIR / "world_cup_2026_team_preview.csv")

    created: list[Path] = []
    titles = features.groupby("team_name", as_index=False)["champion"].sum().query("champion > 0").sort_values("champion")
    _save_bar(titles, "team_name", "champion", "World Cup titles by country", "Titles", "01_titles_by_country.png", "gold")
    created.append(CHART_DIR / "01_titles_by_country.png")

    finals = features.groupby("team_name", as_index=False)["finalist"].sum().query("finalist > 0").sort_values("finalist").tail(15)
    _save_bar(finals, "team_name", "finalist", "Finals reached by country", "Final appearances", "02_finals_by_country.png")
    created.append(CHART_DIR / "02_finals_by_country.png")

    stage_gd = features.groupby(["stage_score", "stage_reached"], as_index=False)["goal_difference"].mean().sort_values("stage_score")
    _save_bar(stage_gd, "stage_reached", "goal_difference", "Average goal difference by stage reached", "Average tournament goal difference", "03_avg_goal_difference_by_stage.png", "green")
    created.append(CHART_DIR / "03_avg_goal_difference_by_stage.png")

    host = features.groupby("is_host", as_index=False).agg(avg_stage=("stage_score", "mean"), semi_rate=("semifinalist", "mean"))
    host["host_label"] = np.where(host["is_host"].eq(1), "Host teams", "Non-host teams")
    _save_bar(host.sort_values("avg_stage"), "host_label", "avg_stage", "Host performance compared with non-hosts", "Average stage score", "04_host_advantage.png", "gold")
    created.append(CHART_DIR / "04_host_advantage.png")

    successful = features[features["stage_score"] >= 4]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(features["goals_for"], features["goals_against"], c="#D0D7DE", alpha=0.45, label="All teams")
    ax.scatter(successful["goals_for"], successful["goals_against"], c=PALETTE["red"], alpha=0.85, label="Semi-finalists or better")
    ax.set_title("Goals scored vs conceded for successful teams", fontsize=14, weight="bold")
    ax.set_xlabel("Goals scored in tournament")
    ax.set_ylabel("Goals conceded in tournament")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "05_goals_for_vs_against_success.png", dpi=180)
    plt.close(fig)
    created.append(CHART_DIR / "05_goals_for_vs_against_success.png")

    defensive = features.assign(group=np.where(features["champion"].eq(1), "Champion", "Non-champion"))
    defensive = defensive.groupby("group", as_index=False)["goals_against_per_match"].mean().sort_values("goals_against_per_match")
    _save_bar(defensive, "group", "goals_against_per_match", "Defensive strength of champions vs non-champions", "Goals conceded per match", "06_defensive_strength_champions.png", "red")
    created.append(CHART_DIR / "06_defensive_strength_champions.png")

    form = features.dropna(subset=["pre_wc_points_per_match"])
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(form["pre_wc_points_per_match"], form["stage_score"], c=PALETTE["blue"], alpha=0.55)
    ax.set_title("Pre-tournament form vs World Cup performance", fontsize=14, weight="bold")
    ax.set_xlabel("Points per match in previous 365 days")
    ax.set_ylabel("Stage score")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "07_pre_tournament_form_vs_stage.png", dpi=180)
    plt.close(fig)
    created.append(CHART_DIR / "07_pre_tournament_form_vs_stage.png")

    model_frame = features.dropna(subset=["pre_wc_points_per_match", "historical_tournaments_before"]).copy()
    columns = ["goal_difference", "goals_against_per_match", "historical_tournaments_before", "pre_wc_points_per_match", "is_host"]
    x = model_frame[columns].fillna(0).to_numpy()
    x = np.column_stack([np.ones(len(x)), x])
    y = model_frame["stage_score"].to_numpy()
    coefficients, *_ = np.linalg.lstsq(x, y, rcond=None)
    model_frame["expected_stage_score"] = x @ coefficients
    model_frame["overperformance"] = model_frame["stage_score"] - model_frame["expected_stage_score"]
    over = model_frame.sort_values("overperformance").tail(12)
    _save_bar(over, "team_name", "overperformance", "Top overperforming team-tournament runs", "Actual stage score minus fitted expectation", "08_overperforming_runs.png", "green")
    created.append(CHART_DIR / "08_overperforming_runs.png")

    confed = features.dropna(subset=["confederation_code"]).groupby("confederation_code", as_index=False)["stage_score"].mean().sort_values("stage_score")
    _save_bar(confed, "confederation_code", "stage_score", "Average World Cup performance by confederation", "Average stage score", "09_confederation_performance.png")
    created.append(CHART_DIR / "09_confederation_performance.png")

    top_2026 = preview_2026.sort_values(["prior_titles", "best_stage_score", "pre_wc_points_per_match"], ascending=False).head(16)
    _save_bar(top_2026.sort_values("prior_titles"), "team_name", "prior_titles", "2026 field: historical titles among qualified teams", "Prior titles", "10_2026_qualified_titles.png", "gold")
    created.append(CHART_DIR / "10_2026_qualified_titles.png")

    interactive = px.line(
        features.sort_values("year"),
        x="year",
        y="stage_score",
        color="team_name",
        hover_data=["stage_reached", "goals_for", "goals_against", "goal_difference"],
        title="Team performance over time",
    )
    interactive.write_html(CHART_DIR / "11_team_performance_over_time.html")
    created.append(CHART_DIR / "11_team_performance_over_time.html")

    notes = [
        "# Chart interpretations",
        "",
        "- Titles and finals are concentrated among a small set of repeat contenders, which supports including historical experience.",
        "- Deeper runs have much higher average goal difference; this is the clearest descriptive factor in the dataset.",
        "- Hosts outperform non-hosts on average, but the effect is not uniform and should not be treated as causal.",
        "- Champions concede fewer goals per match than the field, suggesting defensive floor matters even for elite attacking teams.",
        "- Pre-tournament form has a visible but noisy relationship with stage reached; it is useful context, not a standalone predictor.",
        "- Confederation patterns reflect long-run structural strength and qualification context, but they mix eras and tournament formats.",
        "- The 2026 preview is historical/contextual only because no 2026 World Cup matches have been played yet.",
    ]
    (CHART_DIR / "chart_interpretations.md").write_text("\n".join(notes), encoding="utf-8")
    created.append(CHART_DIR / "chart_interpretations.md")
    return created


if __name__ == "__main__":
    paths = generate_charts()
    print(f"Generated {len(paths)} chart artifacts in {CHART_DIR}")
