-- 03_feature_engineering.sql
-- Team-year features that answer the research question.

CREATE OR REPLACE VIEW team_tournament_metrics AS
SELECT
    year,
    tournament_id,
    team_name,
    COALESCE(confederation_code, 'Unknown') AS confederation_code,
    CAST(is_host AS INTEGER) AS is_host,
    CAST(matches AS INTEGER) AS matches,
    CAST(wins AS INTEGER) AS wins,
    CAST(losses AS INTEGER) AS losses,
    CAST(draws AS INTEGER) AS draws,
    CAST(goals_for AS INTEGER) AS goals_for,
    CAST(goals_against AS INTEGER) AS goals_against,
    CAST(goal_difference AS INTEGER) AS goal_difference,
    win_rate,
    goals_for_per_match,
    goals_against_per_match,
    CAST(historical_tournaments_before AS INTEGER) AS historical_tournaments_before,
    CAST(historical_matches_before AS INTEGER) AS historical_matches_before,
    CAST(historical_wins_before AS INTEGER) AS historical_wins_before,
    CAST(pre_wc_matches AS INTEGER) AS pre_wc_matches,
    pre_wc_points_per_match,
    pre_wc_win_rate,
    pre_wc_goal_diff_per_match,
    performance,
    stage_reached,
    CAST(stage_score AS INTEGER) AS stage_score,
    CAST(champion AS INTEGER) AS champion,
    CAST(finalist AS INTEGER) AS finalist,
    CAST(semifinalist AS INTEGER) AS semifinalist,
    CAST(reached_knockout AS INTEGER) AS reached_knockout
FROM team_tournament_features;

CREATE OR REPLACE VIEW experience_features AS
SELECT
    year,
    team_name,
    historical_tournaments_before,
    historical_matches_before,
    historical_wins_before,
    stage_score
FROM team_tournament_metrics
WHERE historical_tournaments_before >= 0;

CREATE OR REPLACE VIEW preview_2026_ranked AS
SELECT
    team_name,
    group_name,
    confederation_code,
    prior_world_cups,
    prior_titles,
    prior_finals,
    prior_semifinals,
    best_stage_score,
    pre_wc_matches,
    pre_wc_points_per_match,
    pre_wc_win_rate,
    pre_wc_goal_diff_per_match,
    (
        COALESCE(best_stage_score, 0) * 1.20
        + COALESCE(prior_world_cups, 0) * 0.20
        + COALESCE(pre_wc_points_per_match, 0) * 0.80
        + COALESCE(pre_wc_goal_diff_per_match, 0) * 0.35
        + COALESCE(prior_titles, 0) * 0.75
    ) AS readiness_score
FROM world_cup_2026_team_preview;
