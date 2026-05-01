-- 01_create_tables.sql
-- Create DuckDB tables from processed CSV files produced by src/clean_data.py.

CREATE OR REPLACE TABLE matches_clean AS
SELECT *
FROM read_csv_auto('data/processed/matches_clean.csv', HEADER = TRUE, SAMPLE_SIZE = -1);

CREATE OR REPLACE TABLE team_appearances_clean AS
SELECT *
FROM read_csv_auto('data/processed/team_appearances_clean.csv', HEADER = TRUE, SAMPLE_SIZE = -1);

CREATE OR REPLACE TABLE team_results_long AS
SELECT *
FROM read_csv_auto('data/processed/team_results_long.csv', HEADER = TRUE, SAMPLE_SIZE = -1);

CREATE OR REPLACE TABLE pre_tournament_form AS
SELECT *
FROM read_csv_auto('data/processed/pre_tournament_form.csv', HEADER = TRUE, SAMPLE_SIZE = -1);

CREATE OR REPLACE TABLE team_tournament_features AS
SELECT *
FROM read_csv_auto('data/processed/team_tournament_features.csv', HEADER = TRUE, SAMPLE_SIZE = -1);

CREATE OR REPLACE TABLE world_cup_2026_qualified_teams AS
SELECT *
FROM read_csv_auto('data/processed/world_cup_2026_qualified_teams.csv', HEADER = TRUE, SAMPLE_SIZE = -1);

CREATE OR REPLACE TABLE world_cup_2026_team_preview AS
SELECT *
FROM read_csv_auto('data/processed/world_cup_2026_team_preview.csv', HEADER = TRUE, SAMPLE_SIZE = -1);
