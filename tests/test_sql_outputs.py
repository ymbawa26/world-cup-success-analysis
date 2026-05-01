from pathlib import Path
import sys

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from run_sql_analysis import DATABASE_PATH, run_sql_scripts


def test_sql_tables_and_views_are_created():
    run_sql_scripts()
    with duckdb.connect(str(DATABASE_PATH)) as con:
        tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    assert "team_tournament_features" in tables
    assert "team_tournament_metrics" in tables


def test_sql_aggregates_return_expected_columns_and_values():
    run_sql_scripts()
    with duckdb.connect(str(DATABASE_PATH)) as con:
        row = con.execute(
            """
            SELECT wins, losses, draws, goals_for, goals_against, goal_difference
            FROM team_tournament_metrics
            WHERE year = 1930 AND team_name = 'Uruguay'
            """
        ).fetchone()
        impossible = con.execute("SELECT COUNT(*) FROM impossible_records").fetchone()[0]
    assert row == (4, 0, 0, 15, 3, 12)
    assert impossible == 0
