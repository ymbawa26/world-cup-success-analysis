"""Streamlit dashboard for the World Cup success analysis."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from clean_data import build_processed_data  # noqa: E402


PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

st.set_page_config(
    page_title="World Cup Success Analysis",
    page_icon="WC",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --navy: #0B1220;
        --ink: #111827;
        --muted: #64748B;
        --line: #E2E8F0;
        --card: #FFFFFF;
        --blue: #2563EB;
        --gold: #B45309;
        --green: #047857;
    }
    html, body, .stApp, .main, [data-testid="stAppViewContainer"] {
        background: #F8FAFC !important;
        color: var(--ink) !important;
    }
    [data-testid="stHeader"] {
        background: rgba(248, 250, 252, 0.94) !important;
    }
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background: #F1F5F9 !important;
        color: var(--ink) !important;
    }
    h1, h2, h3, h4, h5, h6, p, label, div, span {
        color: var(--ink);
        letter-spacing: 0;
    }
    h1 { font-size: 2.2rem; font-weight: 800; margin-bottom: .2rem; }
    h2 { font-size: 1.4rem; font-weight: 750; margin-top: 1.5rem; }
    .subtitle { color: var(--muted); font-size: 1.02rem; max-width: 960px; }
    .kpi-card {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }
    .kpi-label { color: var(--muted); font-size: .78rem; text-transform: uppercase; font-weight: 700; }
    .kpi-value { color: var(--navy); font-size: 1.75rem; font-weight: 800; margin-top: 2px; }
    .insight {
        background: #FFFFFF;
        border-left: 4px solid var(--blue);
        padding: 14px 16px;
        margin: 10px 0;
        border-radius: 6px;
        border-top: 1px solid var(--line);
        border-right: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 14px 16px;
    }
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricDelta"] div {
        color: var(--ink) !important;
    }
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        color: var(--ink) !important;
    }
    [data-baseweb="select"],
    [data-baseweb="select"] div,
    [data-baseweb="popover"],
    [data-baseweb="popover"] div,
    [data-baseweb="menu"],
    [data-baseweb="menu"] li {
        background-color: #FFFFFF !important;
        color: var(--ink) !important;
    }
    [data-baseweb="tag"] {
        background-color: #2563EB !important;
    }
    [data-baseweb="tag"] span,
    [data-baseweb="tag"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] * {
        color: var(--ink) !important;
    }
    .js-plotly-plot,
    .js-plotly-plot .plotly,
    .js-plotly-plot text {
        color: var(--ink) !important;
        fill: var(--ink) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_optional_csv(filename: str) -> pd.DataFrame:
    path = PROCESSED_DIR / filename
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not (PROCESSED_DIR / "team_tournament_features.csv").exists():
        build_processed_data()
    features = pd.read_csv(PROCESSED_DIR / "team_tournament_features.csv")
    preview = pd.read_csv(PROCESSED_DIR / "world_cup_2026_team_preview.csv")
    matches = pd.read_csv(PROCESSED_DIR / "matches_clean.csv")
    model_summary = load_optional_csv("baseline_model_summary.csv")
    model_importance = load_optional_csv("baseline_model_feature_importance.csv")
    model_predictions = load_optional_csv("baseline_model_predictions.csv")
    return features, preview, matches, model_summary, model_importance, model_predictions


features, preview_2026, matches, model_summary, model_importance, model_predictions = load_data()


def style_fig(fig):
    """Force a readable light chart theme independent of Streamlit/browser theme."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={"color": "#111827", "family": "Inter, Arial, sans-serif"},
        title={"font": {"color": "#111827", "size": 16}},
        legend={"font": {"color": "#111827"}, "bgcolor": "rgba(255,255,255,0.92)"},
        margin={"l": 20, "r": 20, "t": 70, "b": 50},
    )
    fig.update_xaxes(
        title_font={"color": "#475569"},
        tickfont={"color": "#475569"},
        gridcolor="#E2E8F0",
        zerolinecolor="#CBD5E1",
    )
    fig.update_yaxes(
        title_font={"color": "#475569"},
        tickfont={"color": "#475569"},
        gridcolor="#E2E8F0",
        zerolinecolor="#CBD5E1",
    )
    return fig

st.title("Predicting World Cup Success")
st.markdown(
    "<div class='subtitle'>A SQL and Python analysis of which measurable factors are most associated with deep FIFA World Cup runs: goal difference, defense, attacking output, host advantage, experience, region, knockout efficiency, and pre-tournament form.</div>",
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Dashboard",
    ["Overview", "Team explorer", "Factor analysis", "Comparison", "2026 field", "Model baseline", "Insights"],
)


def kpi(label: str, value: str) -> None:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>", unsafe_allow_html=True)


if page == "Overview":
    tournaments = features["year"].nunique()
    teams = features["team_name"].nunique()
    total_matches = matches["match_id"].nunique()
    total_goals = int(matches["home_team_score"].sum() + matches["away_team_score"].sum())
    most_successful = (
        features.groupby("team_name")["champion"].sum().sort_values(ascending=False).index[0]
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi("Tournaments", f"{tournaments}")
    with c2:
        kpi("Teams", f"{teams}")
    with c3:
        kpi("Matches", f"{total_matches:,}")
    with c4:
        kpi("Goals", f"{total_goals:,}")
    with c5:
        kpi("Most titles", most_successful)

    col_a, col_b = st.columns([1.1, 1])
    with col_a:
        titles = features.groupby("team_name", as_index=False)["champion"].sum().query("champion > 0").sort_values("champion", ascending=False)
        fig = px.bar(titles, x="champion", y="team_name", orientation="h", title="World Cup titles by country", color="champion", color_continuous_scale="Blues")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_title="Titles", yaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig), width="stretch")
    with col_b:
        stage = features.groupby("stage_reached", as_index=False)["goal_difference"].mean().sort_values("goal_difference")
        fig = px.bar(stage, x="goal_difference", y="stage_reached", orientation="h", title="Average goal difference by best finish", color="goal_difference", color_continuous_scale="Greens")
        fig.update_layout(xaxis_title="Average goal difference", yaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig), width="stretch")

elif page == "Team explorer":
    team = st.selectbox("Select team", sorted(features["team_name"].unique()), index=sorted(features["team_name"].unique()).index("Brazil"))
    team_df = features[features["team_name"].eq(team)].sort_values("year")
    totals = team_df[["champion", "finalist", "semifinalist", "wins", "losses", "draws", "goals_for", "goals_against", "goal_difference"]].sum()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Titles", int(totals["champion"]))
    c2.metric("Finals", int(totals["finalist"]))
    c3.metric("Semi-finals/top four", int(totals["semifinalist"]))
    c4.metric("Goal difference", int(totals["goal_difference"]))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Wins", int(totals["wins"]))
    c6.metric("Losses", int(totals["losses"]))
    c7.metric("Draws", int(totals["draws"]))
    c8.metric("Goals", f"{int(totals['goals_for'])}-{int(totals['goals_against'])}")

    fig = px.line(team_df, x="year", y="stage_score", markers=True, title=f"{team}: performance over time", hover_data=["stage_reached", "goal_difference"])
    fig.update_layout(yaxis_title="Stage score", xaxis_title="World Cup year")
    st.plotly_chart(style_fig(fig), width="stretch")

    goals = team_df.melt(id_vars=["year"], value_vars=["goals_for", "goals_against"], var_name="metric", value_name="goals")
    fig = px.bar(goals, x="year", y="goals", color="metric", barmode="group", title=f"{team}: goals scored and conceded by tournament", color_discrete_map={"goals_for": "#2563EB", "goals_against": "#DC2626"})
    fig.update_layout(xaxis_title="World Cup year", yaxis_title="Goals")
    st.plotly_chart(style_fig(fig), width="stretch")

elif page == "Factor analysis":
    factor = st.selectbox(
        "Factor",
        ["goal_difference", "goals_for_per_match", "goals_against_per_match", "historical_tournaments_before", "pre_wc_points_per_match", "is_host"],
    )
    filtered = features.dropna(subset=[factor]).copy()
    fig = px.scatter(
        filtered,
        x=factor,
        y="stage_score",
        color="confederation_code",
        hover_data=["team_name", "year", "stage_reached"],
        title=f"{factor.replace('_', ' ').title()} vs World Cup performance",
    )
    fig.update_layout(yaxis_title="Stage score")
    st.plotly_chart(style_fig(fig), width="stretch")

    col_a, col_b = st.columns(2)
    with col_a:
        host = features.groupby("is_host", as_index=False).agg(avg_stage=("stage_score", "mean"), semi_rate=("semifinalist", "mean"))
        host["label"] = host["is_host"].map({0: "Non-host", 1: "Host"})
        fig = px.bar(host, x="label", y="avg_stage", title="Host advantage: average stage score", color="label", color_discrete_sequence=["#64748B", "#B45309"])
        fig.update_layout(xaxis_title="", yaxis_title="Average stage score", showlegend=False)
        st.plotly_chart(style_fig(fig), width="stretch")
    with col_b:
        confed = features.groupby("confederation_code", as_index=False)["stage_score"].mean().sort_values("stage_score", ascending=False)
        fig = px.bar(confed, x="confederation_code", y="stage_score", title="Confederation performance comparison", color="stage_score", color_continuous_scale="Blues")
        fig.update_layout(xaxis_title="Confederation", yaxis_title="Average stage score", coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig), width="stretch")

elif page == "Comparison":
    teams = sorted(features["team_name"].unique())
    left, right = st.columns(2)
    team_a = left.selectbox("Team A", teams, index=teams.index("Brazil"))
    team_b = right.selectbox("Team B", teams, index=teams.index("Argentina"))
    comp = []
    for team in [team_a, team_b]:
        frame = features[features["team_name"].eq(team)]
        comp.append(
            {
                "team": team,
                "titles": int(frame["champion"].sum()),
                "finals": int(frame["finalist"].sum()),
                "total_wins": int(frame["wins"].sum()),
                "win_rate": frame["wins"].sum() / frame["matches"].sum(),
                "avg_goal_difference": frame["goal_difference"].mean(),
                "best_finish_score": int(frame["stage_score"].max()),
                "recent_avg_stage": frame.sort_values("year").tail(3)["stage_score"].mean(),
            }
        )
    comp_df = pd.DataFrame(comp)
    st.dataframe(comp_df, width="stretch", hide_index=True)
    fig = px.bar(comp_df.melt(id_vars="team"), x="variable", y="value", color="team", barmode="group", title="Side-by-side comparison")
    fig.update_layout(xaxis_title="", yaxis_title="Value")
    st.plotly_chart(style_fig(fig), width="stretch")

elif page == "2026 field":
    st.markdown("The 2026 page is a preview only. It uses verified qualified teams/groups and historical plus recent-form features; it does not use any 2026 World Cup match results.")
    group_filter = st.multiselect("Groups", sorted(preview_2026["group_name"].unique()), default=sorted(preview_2026["group_name"].unique()))
    filtered = preview_2026[preview_2026["group_name"].isin(group_filter)] if group_filter else preview_2026
    table = filtered.sort_values(["group_name", "team_name"])[
        ["group_name", "team_name", "confederation_code", "prior_world_cups", "prior_titles", "prior_finals", "pre_wc_points_per_match", "pre_wc_goal_diff_per_match"]
    ].copy()
    table = table.rename(
        columns={
            "group_name": "Group",
            "team_name": "Team",
            "confederation_code": "Confed.",
            "prior_world_cups": "Prior WCs",
            "prior_titles": "Titles",
            "prior_finals": "Finals",
            "pre_wc_points_per_match": "Recent PPG",
            "pre_wc_goal_diff_per_match": "Recent GD/match",
        }
    )
    for column in ["Recent PPG", "Recent GD/match"]:
        table[column] = table[column].round(2)
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
    )
    fig = px.scatter(
        preview_2026,
        x="prior_world_cups",
        y="pre_wc_points_per_match",
        color="confederation_code",
        size="prior_titles",
        hover_data=["team_name", "group_name", "best_stage_score"],
        title="2026 qualified teams: experience and recent form",
    )
    fig.update_layout(xaxis_title="Prior World Cups", yaxis_title="Pre-World Cup points per match")
    st.plotly_chart(style_fig(fig), width="stretch")

elif page == "Model baseline":
    st.subheader("Leakage-safe semifinal baseline")
    st.write(
        "This model estimates whether a team reaches the semifinals/top four. It trains on tournaments from 1966-2006 and tests on 2010-2022, using only host status, past World Cup experience, pre-tournament form, and confederation."
    )
    if model_summary.empty or model_importance.empty or model_predictions.empty:
        st.warning("Model outputs have not been generated yet. Run `make run` to export baseline model files.")
    else:
        row = model_summary.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Target", row["target"])
        c2.metric("Train years", row["train_years"])
        c3.metric("Test years", row["test_years"])
        c4.metric("Accuracy", f"{row['accuracy']:.3f}")

        top_features = model_importance.assign(abs_weight=model_importance["coefficient"].abs()).sort_values("abs_weight", ascending=False).head(12)
        fig = px.bar(
            top_features.sort_values("coefficient"),
            x="coefficient",
            y="feature",
            orientation="h",
            title="Largest logistic-regression coefficients",
            color="coefficient",
            color_continuous_scale="RdBu",
        )
        fig.update_layout(xaxis_title="Coefficient", yaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig), width="stretch")

        years = sorted(model_predictions["year"].unique())
        year = st.selectbox("Prediction year", years, index=len(years) - 1)
        shown = model_predictions[model_predictions["year"].eq(year)].sort_values("semifinal_probability", ascending=False)
        shown = shown[["team_name", "stage_reached", "semifinalist", "predicted_semifinalist", "semifinal_probability"]].copy()
        shown["semifinal_probability"] = shown["semifinal_probability"].round(3)
        shown = shown.rename(
            columns={
                "team_name": "Team",
                "stage_reached": "Actual finish",
                "semifinalist": "Actual top four",
                "predicted_semifinalist": "Predicted top four",
                "semifinal_probability": "Probability",
            }
        )
        st.dataframe(shown, hide_index=True, width="stretch")

else:
    st.subheader("Findings grounded in the data")
    findings = [
        "Goal difference has the strongest descriptive relationship with deep runs. Teams that reach finals and win titles usually separate themselves by both scoring and suppressing opponents.",
        "Defense is a consistent floor. Champions concede fewer goals per match than the overall field, which suggests that elite attacking output is rarely enough without defensive control.",
        "Host teams perform better on average, but this dashboard treats that as an association. Host advantage can reflect travel, crowd, familiarity, and sometimes team quality.",
        "Historical experience matters, but it is not destiny. Several strong runs come from teams with limited prior tournament history, especially in unusual formats or expanding fields.",
        "Pre-tournament form is useful but noisy. It should be read as context because friendly schedules, opponent strength, and missing future fixtures vary by team.",
    ]
    for item in findings:
        st.markdown(f"<div class='insight'>{item}</div>", unsafe_allow_html=True)
    st.subheader("What this does not prove")
    st.write(
        "This project does not claim to predict the 2026 winner. The analysis is observational, tournament formats change over time, and simple team-level features cannot fully capture injuries, tactics, player quality, draw difficulty, or match state."
    )
    st.subheader("Limitations")
    st.write(
        "Stage labels before the modern knockout era are normalized into comparable scores, which is necessary for analysis but imperfect. The 2026 field is verified from current sources, but the tournament has not happened yet, so 2026 records are preview-only."
    )
