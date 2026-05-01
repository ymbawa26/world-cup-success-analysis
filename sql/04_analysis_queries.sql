-- 04_analysis_queries.sql
-- Readable portfolio queries for factor analysis.

CREATE OR REPLACE VIEW stage_factor_summary AS
SELECT
    stage_score,
    stage_reached,
    COUNT(*) AS team_tournaments,
    AVG(goal_difference) AS avg_goal_difference,
    AVG(goals_for_per_match) AS avg_goals_for_per_match,
    AVG(goals_against_per_match) AS avg_goals_against_per_match,
    AVG(historical_tournaments_before) AS avg_prior_world_cups,
    AVG(pre_wc_points_per_match) AS avg_pre_wc_points_per_match
FROM team_tournament_metrics
GROUP BY stage_score, stage_reached;

CREATE OR REPLACE VIEW host_advantage_summary AS
SELECT
    is_host,
    COUNT(*) AS team_tournaments,
    AVG(stage_score) AS avg_stage_score,
    AVG(semifinalist) AS semifinal_rate,
    AVG(finalist) AS final_rate,
    AVG(champion) AS title_rate,
    AVG(goal_difference) AS avg_goal_difference
FROM team_tournament_metrics
GROUP BY is_host;

CREATE OR REPLACE VIEW confederation_summary AS
SELECT
    confederation_code,
    COUNT(*) AS team_tournaments,
    AVG(stage_score) AS avg_stage_score,
    AVG(reached_knockout) AS knockout_rate,
    AVG(semifinalist) AS semifinal_rate,
    AVG(goal_difference) AS avg_goal_difference
FROM team_tournament_metrics
GROUP BY confederation_code;

CREATE OR REPLACE VIEW country_success_summary AS
SELECT
    team_name,
    COUNT(*) AS tournaments_played,
    SUM(champion) AS titles,
    SUM(finalist) AS finals,
    SUM(semifinalist) AS semifinals,
    SUM(wins) AS total_wins,
    SUM(losses) AS total_losses,
    SUM(draws) AS total_draws,
    SUM(goals_for) AS goals_for,
    SUM(goals_against) AS goals_against,
    SUM(goal_difference) AS goal_difference,
    AVG(win_rate) AS avg_win_rate,
    MAX(stage_score) AS best_stage_score
FROM team_tournament_metrics
GROUP BY team_name;

CREATE OR REPLACE VIEW factor_correlations AS
SELECT
    corr(stage_score, goal_difference) AS corr_stage_goal_difference,
    corr(stage_score, goals_for_per_match) AS corr_stage_attack,
    corr(stage_score, goals_against_per_match) AS corr_stage_defense_conceded,
    corr(stage_score, historical_tournaments_before) AS corr_stage_experience,
    corr(stage_score, pre_wc_points_per_match) AS corr_stage_recent_form
FROM team_tournament_metrics
WHERE pre_wc_points_per_match IS NOT NULL;
