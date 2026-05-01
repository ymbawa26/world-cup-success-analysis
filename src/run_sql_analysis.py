"""Run DuckDB SQL scripts and export analysis tables."""

from __future__ import annotations

from pathlib import Path

import duckdb

from clean_data import PROJECT_ROOT, build_processed_data


SQL_DIR = PROJECT_ROOT / "sql"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_PATH = PROCESSED_DIR / "world_cup_success.duckdb"

EXPORT_QUERIES = {
    "sql_team_tournament_metrics.csv": "SELECT * FROM team_tournament_metrics ORDER BY year, team_name",
    "sql_stage_factor_summary.csv": "SELECT * FROM stage_factor_summary ORDER BY stage_score",
    "sql_host_advantage_summary.csv": "SELECT * FROM host_advantage_summary ORDER BY is_host DESC",
    "sql_confederation_summary.csv": "SELECT * FROM confederation_summary ORDER BY avg_stage_score DESC",
    "sql_2026_preview_ranked.csv": "SELECT * FROM preview_2026_ranked ORDER BY readiness_score DESC",
}


def run_sql_scripts(database_path: Path = DATABASE_PATH) -> Path:
    """Build DuckDB tables/views from the processed data and export results."""
    if not (PROCESSED_DIR / "team_tournament_features.csv").exists():
        build_processed_data()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(database_path)) as con:
        con.execute("SET threads TO 4;")
        for script_name in [
            "01_create_tables.sql",
            "02_cleaning_queries.sql",
            "03_feature_engineering.sql",
            "04_analysis_queries.sql",
        ]:
            sql = (SQL_DIR / script_name).read_text(encoding="utf-8")
            con.execute(sql)
        for filename, query in EXPORT_QUERIES.items():
            con.execute(f"COPY ({query}) TO '{(PROCESSED_DIR / filename).as_posix()}' (HEADER, DELIMITER ',')")
    return database_path


if __name__ == "__main__":
    db_path = run_sql_scripts()
    print(f"DuckDB analysis complete: {db_path}")
