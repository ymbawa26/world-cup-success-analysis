-- 02_cleaning_queries.sql
-- Validation-oriented cleaning views used by the analysis and tests.

CREATE OR REPLACE VIEW valid_team_appearances AS
SELECT
    tournament_id,
    year,
    match_id,
    stage_name,
    team_name,
    opponent_name,
    CAST(goals_for AS INTEGER) AS goals_for,
    CAST(goals_against AS INTEGER) AS goals_against,
    CAST(goal_differential AS INTEGER) AS goal_difference,
    CAST(win AS INTEGER) AS win,
    CAST(lose AS INTEGER) AS loss,
    CAST(draw AS INTEGER) AS draw,
    outcome
FROM team_appearances_clean
WHERE goals_for >= 0
  AND goals_against >= 0
  AND outcome IN ('win', 'loss', 'draw');

CREATE OR REPLACE VIEW impossible_records AS
SELECT *
FROM valid_team_appearances
WHERE goals_for < 0
   OR goals_against < 0
   OR win + loss + draw <> 1;

CREATE OR REPLACE VIEW clean_match_counts AS
SELECT
    year,
    COUNT(DISTINCT match_id) AS matches,
    COUNT(*) AS team_match_rows
FROM valid_team_appearances
GROUP BY year;
